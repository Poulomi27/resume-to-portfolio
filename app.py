from flask import Flask, request, render_template, send_file, jsonify, url_for
import os
import re
import pdfplumber
from pathlib import Path
from werkzeug.utils import secure_filename
import secrets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'generated_portfolios'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_resume_data(pdf_path):
    """Extract structured data from resume PDF"""
    data = {
        "name": "",
        "title": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "website": "",
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": []
    }
    
    full_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    
    lines = full_text.split('\n')
    
    # Extract contact information
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    github_pattern = r'github\.com/[\w-]+'
    
    for line in lines[:20]:
        if not data["email"] and re.search(email_pattern, line):
            data["email"] = re.search(email_pattern, line).group()
        if not data["phone"] and re.search(phone_pattern, line):
            data["phone"] = re.search(phone_pattern, line).group()
        if not data["linkedin"] and re.search(linkedin_pattern, line, re.IGNORECASE):
            data["linkedin"] = "https://" + re.search(linkedin_pattern, line, re.IGNORECASE).group()
        if not data["github"] and re.search(github_pattern, line, re.IGNORECASE):
            data["github"] = "https://" + re.search(github_pattern, line, re.IGNORECASE).group()
    
    # Extract name
    for line in lines[:10]:
        if line.strip() and len(line.strip()) > 3 and len(line.strip()) < 50:
            if not any(char.isdigit() for char in line) and '@' not in line:
                data["name"] = line.strip()
                break
    
    # Parse sections
    current_section = None
    section_content = []
    
    experience_keywords = ['experience', 'work history', 'employment', 'professional experience']
    education_keywords = ['education', 'academic background', 'qualifications']
    skills_keywords = ['skills', 'technical skills', 'expertise', 'competencies']
    projects_keywords = ['projects', 'portfolio', 'work samples']
    
    for line in lines:
        line_lower = line.lower().strip()
        
        if any(keyword in line_lower for keyword in experience_keywords):
            if current_section and section_content:
                parse_section(data, current_section, section_content)
            current_section = 'experience'
            section_content = []
        elif any(keyword in line_lower for keyword in education_keywords):
            if current_section and section_content:
                parse_section(data, current_section, section_content)
            current_section = 'education'
            section_content = []
        elif any(keyword in line_lower for keyword in skills_keywords):
            if current_section and section_content:
                parse_section(data, current_section, section_content)
            current_section = 'skills'
            section_content = []
        elif any(keyword in line_lower for keyword in projects_keywords):
            if current_section and section_content:
                parse_section(data, current_section, section_content)
            current_section = 'projects'
            section_content = []
        elif line.strip():
            section_content.append(line)
    
    if current_section and section_content:
        parse_section(data, current_section, section_content)
    
    # Extract title
    if not data["title"]:
        for line in lines[1:10]:
            if line.strip() and len(line.strip()) > 5 and '@' not in line and not any(char.isdigit() for char in line[:3]):
                data["title"] = line.strip()
                break
    
    return data

def parse_section(data, section_type, content):
    """Parse different resume sections"""
    if section_type == 'experience':
        current_job = {}
        for line in content:
            line = line.strip()
            if not line:
                if current_job:
                    data['experience'].append(current_job)
                    current_job = {}
                continue
            
            date_pattern = r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4})'
            if re.search(date_pattern, line):
                if 'dates' not in current_job:
                    current_job['dates'] = line
            elif not current_job.get('title'):
                current_job['title'] = line
            elif not current_job.get('company'):
                current_job['company'] = line
            else:
                if 'description' not in current_job:
                    current_job['description'] = []
                current_job['description'].append(line)
        
        if current_job:
            data['experience'].append(current_job)
    
    elif section_type == 'education':
        current_edu = {}
        for line in content:
            line = line.strip()
            if not line:
                if current_edu:
                    data['education'].append(current_edu)
                    current_edu = {}
                continue
            
            if not current_edu.get('degree'):
                current_edu['degree'] = line
            elif not current_edu.get('institution'):
                current_edu['institution'] = line
            else:
                if 'details' not in current_edu:
                    current_edu['details'] = []
                current_edu['details'].append(line)
        
        if current_edu:
            data['education'].append(current_edu)
    
    elif section_type == 'skills':
        skills_text = ' '.join(content)
        skill_items = re.split(r'[,;•·\n]', skills_text)
        data['skills'] = [s.strip() for s in skill_items if s.strip() and len(s.strip()) > 1]
    
    elif section_type == 'projects':
        current_project = {}
        for line in content:
            line = line.strip()
            if not line:
                if current_project:
                    data['projects'].append(current_project)
                    current_project = {}
                continue
            
            if not current_project.get('name'):
                current_project['name'] = line
            else:
                if 'description' not in current_project:
                    current_project['description'] = []
                current_project['description'].append(line)
        
        if current_project:
            data['projects'].append(current_project)

def generate_portfolio_html(data):
    """Generate portfolio HTML content"""
    name = data.get('name', 'Professional Portfolio')
    title = data.get('title', 'Professional')
    email = data.get('email', '')
    phone = data.get('phone', '')
    linkedin = data.get('linkedin', '')
    github = data.get('github', '')
    
    # Build sections
    experience_html = ""
    for exp in data.get('experience', []):
        desc_items = ""
        if 'description' in exp and exp['description']:
            for item in exp['description']:
                desc_items += f"            <li>{item}</li>\n"
        
        experience_html += f"""
        <div class="experience-item">
          <div class="item-header">
            <div>
              <h3>{exp.get('title', 'Position')}</h3>
              <p class="company">{exp.get('company', 'Company')}</p>
            </div>
            <span class="dates">{exp.get('dates', '')}</span>
          </div>
          <ul class="description">
{desc_items}          </ul>
        </div>
"""
    
    education_html = ""
    for edu in data.get('education', []):
        education_html += f"""
        <div class="education-item">
          <h3>{edu.get('degree', 'Degree')}</h3>
          <p class="institution">{edu.get('institution', 'Institution')}</p>
        </div>
"""
    
    skills_html = ""
    for skill in data.get('skills', [])[:20]:
        skills_html += f'        <span class="skill-tag">{skill}</span>\n'
    
    projects_html = ""
    for proj in data.get('projects', []):
        desc_text = ' '.join(proj.get('description', [])) if 'description' in proj else ''
        projects_html += f"""
        <div class="project-item">
          <h3>{proj.get('name', 'Project')}</h3>
          <p>{desc_text}</p>
        </div>
"""
    
    contact_links = ""
    if email:
        contact_links += f'          <a href="mailto:{email}" class="contact-link">✉ Email</a>\n'
    if phone:
        contact_links += f'          <a href="tel:{phone}" class="contact-link">📱 Phone</a>\n'
    if linkedin:
        contact_links += f'          <a href="{linkedin}" target="_blank" class="contact-link">💼 LinkedIn</a>\n'
    if github:
        contact_links += f'          <a href="{github}" target="_blank" class="contact-link">💻 GitHub</a>\n'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} - Portfolio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@300;400;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    :root {{
      --primary: #1a1a2e; --secondary: #16213e; --accent: #e94560;
      --accent-light: #ff6b88; --text: #f0f0f0; --text-dim: #a0a0a0;
      --bg: #0f0f1e; --card-bg: #1a1a2e;
    }}
    body {{ font-family: 'Crimson Pro', serif; background: var(--bg); color: var(--text); line-height: 1.7; overflow-x: hidden; }}
    .background-grid {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(rgba(233, 69, 96, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(233, 69, 96, 0.03) 1px, transparent 1px); background-size: 50px 50px; pointer-events: none; z-index: 0; }}
    .container {{ max-width: 1200px; margin: 0 auto; padding: 0 2rem; position: relative; z-index: 1; }}
    header {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; text-align: center; position: relative; overflow: hidden; }}
    .hero-content {{ animation: fadeInUp 1s ease-out; }}
    .name {{ font-size: clamp(3rem, 8vw, 7rem); font-weight: 700; margin-bottom: 1rem; background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; letter-spacing: -0.02em; }}
    .tagline {{ font-size: clamp(1.5rem, 3vw, 2.5rem); font-weight: 300; margin-bottom: 3rem; color: var(--text-dim); font-family: 'DM Mono', monospace; }}
    .contact-links {{ display: flex; gap: 1.5rem; justify-content: center; flex-wrap: wrap; }}
    .contact-link {{ padding: 0.8rem 2rem; background: rgba(233, 69, 96, 0.1); border: 2px solid var(--accent); color: var(--text); text-decoration: none; border-radius: 50px; font-family: 'DM Mono', monospace; font-size: 0.9rem; transition: all 0.3s ease; display: inline-block; }}
    .contact-link:hover {{ background: var(--accent); transform: translateY(-2px); box-shadow: 0 10px 30px rgba(233, 69, 96, 0.3); }}
    section {{ padding: 6rem 0; opacity: 0; animation: fadeIn 1s ease-out forwards; animation-delay: 0.3s; }}
    .section-title {{ font-size: clamp(2.5rem, 5vw, 4rem); font-weight: 700; margin-bottom: 3rem; position: relative; display: inline-block; }}
    .section-title::after {{ content: ''; position: absolute; bottom: -10px; left: 0; width: 60%; height: 4px; background: linear-gradient(90deg, var(--accent), transparent); }}
    .experience-item, .education-item, .project-item {{ background: var(--card-bg); padding: 2rem; margin-bottom: 2rem; border-radius: 12px; border-left: 4px solid var(--accent); transition: all 0.3s ease; position: relative; overflow: hidden; }}
    .experience-item::before, .education-item::before, .project-item::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(233, 69, 96, 0.05), transparent); opacity: 0; transition: opacity 0.3s ease; }}
    .experience-item:hover::before, .education-item:hover::before, .project-item:hover::before {{ opacity: 1; }}
    .experience-item:hover, .education-item:hover, .project-item:hover {{ transform: translateX(10px); box-shadow: -5px 0 20px rgba(233, 69, 96, 0.2); }}
    .item-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 1rem; }}
    .experience-item h3, .education-item h3, .project-item h3 {{ font-size: 1.8rem; color: var(--accent-light); margin-bottom: 0.5rem; }}
    .company, .institution {{ font-size: 1.2rem; color: var(--text-dim); font-family: 'DM Mono', monospace; }}
    .dates {{ font-family: 'DM Mono', monospace; font-size: 0.9rem; color: var(--text-dim); background: rgba(233, 69, 96, 0.1); padding: 0.3rem 1rem; border-radius: 20px; }}
    .description {{ list-style: none; margin-top: 1rem; }}
    .description li {{ position: relative; padding-left: 1.5rem; margin-bottom: 0.8rem; color: var(--text-dim); }}
    .description li::before {{ content: '▹'; position: absolute; left: 0; color: var(--accent); font-weight: bold; }}
    .skills-container {{ display: flex; flex-wrap: wrap; gap: 1rem; }}
    .skill-tag {{ background: rgba(233, 69, 96, 0.1); color: var(--text); padding: 0.6rem 1.5rem; border-radius: 25px; font-size: 0.95rem; font-family: 'DM Mono', monospace; border: 1px solid rgba(233, 69, 96, 0.3); transition: all 0.3s ease; display: inline-block; }}
    .skill-tag:hover {{ background: var(--accent); transform: translateY(-3px); box-shadow: 0 5px 15px rgba(233, 69, 96, 0.3); }}
    footer {{ text-align: center; padding: 3rem 0; color: var(--text-dim); font-family: 'DM Mono', monospace; font-size: 0.9rem; border-top: 1px solid rgba(233, 69, 96, 0.1); }}
    @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @media (max-width: 768px) {{ .item-header {{ flex-direction: column; }} section {{ padding: 4rem 0; }} }}
  </style>
</head>
<body>
  <div class="background-grid"></div>
  <header>
    <div class="hero-content">
      <h1 class="name">{name}</h1>
      <p class="tagline">{title}</p>
      <div class="contact-links">{contact_links}</div>
    </div>
  </header>
  <div class="container">
    {'<section id="experience"><h2 class="section-title">Experience</h2>' + experience_html + '</section>' if experience_html else ''}
    {'<section id="projects"><h2 class="section-title">Projects</h2>' + projects_html + '</section>' if projects_html else ''}
    {'<section id="education"><h2 class="section-title">Education</h2>' + education_html + '</section>' if education_html else ''}
    {'<section id="skills"><h2 class="section-title">Skills</h2><div class="skills-container">' + skills_html + '</div></section>' if skills_html else ''}
  </div>
  <footer><p>© {name} · Portfolio generated from resume</p></footer>
</body>
</html>"""
    
    return html

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract data from PDF
        resume_data = extract_resume_data(filepath)
        
        # Generate portfolio HTML
        portfolio_html = generate_portfolio_html(resume_data)
        
        # Save portfolio
        output_filename = f"{Path(filename).stem}_portfolio.html"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(portfolio_html)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'preview_url': url_for('preview_portfolio', filename=output_filename),
            'download_url': url_for('download_portfolio', filename=output_filename)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<filename>')
def preview_portfolio(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename))

@app.route('/download/<filename>')
def download_portfolio(filename):
    return send_file(
        os.path.join(app.config['OUTPUT_FOLDER'], filename),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
