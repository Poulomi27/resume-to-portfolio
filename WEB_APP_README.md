# Resume to Portfolio Web Generator

A beautiful web application that transforms PDF resumes into stunning portfolio websites instantly!

## Features

✨ **Drag & Drop Interface** - Simply drop your PDF resume  
🎨 **Beautiful Design** - Modern, animated UI with glassmorphism effects  
⚡ **Instant Generation** - Get your portfolio in seconds  
📱 **Responsive** - Works perfectly on all devices  
👁️ **Live Preview** - See your portfolio before downloading  
⬇️ **Easy Download** - Get your HTML file with one click  
🔒 **Privacy First** - All processing happens locally  

## Screenshots

The interface features:
- Animated gradient background
- Drag-and-drop file upload
- Live portfolio preview
- One-click download
- Mobile-responsive design

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install Flask pdfplumber Werkzeug
```

### 2. Run the Application

```bash
python app.py
```

### 3. Open in Browser

Navigate to:
```
http://localhost:5000
```

## How to Use

1. **Upload Resume**
   - Drag and drop your PDF resume onto the upload area
   - Or click to browse and select your file

2. **Wait for Processing**
   - The app will automatically extract information
   - Processing takes 2-5 seconds

3. **Preview Your Portfolio**
   - View the generated portfolio in the preview window
   - Check that all information was extracted correctly

4. **Download**
   - Click "Download HTML" to save your portfolio
   - The file is ready to use - just open it in any browser!

## What Gets Extracted

The application intelligently extracts:

- ✅ **Personal Information**
  - Name
  - Job title/role
  - Email address
  - Phone number
  - LinkedIn profile
  - GitHub profile

- ✅ **Professional Experience**
  - Job titles
  - Company names
  - Employment dates
  - Job descriptions and achievements

- ✅ **Education**
  - Degrees
  - Institutions
  - Graduation dates

- ✅ **Skills**
  - Technical skills
  - Tools and technologies
  - Languages and frameworks

- ✅ **Projects**
  - Project names
  - Descriptions
  - Technologies used

## Portfolio Features

The generated portfolio includes:

- 🎨 Modern dark theme with gradient accents
- ✨ Smooth scroll animations
- 💫 Hover effects on cards
- 📱 Fully responsive design
- 🎯 Clean, professional layout
- 🔗 Clickable contact links
- ⚡ Fast loading (single HTML file)

## File Structure

```
resume-portfolio-generator/
├── app.py                      # Flask backend
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Frontend interface
├── uploads/                   # Temporary upload folder
└── generated_portfolios/      # Output folder
```

## Technical Details

### Backend (Flask)
- Handles file uploads
- Extracts text from PDF using pdfplumber
- Parses resume sections with regex
- Generates HTML portfolio
- Serves preview and download

### Frontend (HTML/CSS/JS)
- Drag-and-drop file upload
- Real-time status updates
- Animated UI with smooth transitions
- Live portfolio preview in iframe
- Responsive design with CSS Grid

## Configuration

You can customize the app by editing `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size (16MB)
app.config['UPLOAD_FOLDER'] = 'uploads'              # Upload directory
app.config['OUTPUT_FOLDER'] = 'generated_portfolios'  # Output directory
```

## Customizing the Portfolio Design

The generated portfolio uses CSS variables for easy customization. To change colors, edit the HTML template generation in `app.py`:

```css
:root {
  --primary: #1a1a2e;      /* Main background */
  --accent: #e94560;       /* Accent color */
  --text: #f0f0f0;         /* Text color */
}
```

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

**Using Gunicorn:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Using Docker:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

**Deploy to Cloud:**
- Heroku
- Railway
- Render
- DigitalOcean
- AWS/GCP/Azure

## Troubleshooting

### "No module named 'flask'"
```bash
pip install Flask
```

### "No module named 'pdfplumber'"
```bash
pip install pdfplumber
```

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

### PDF not parsing correctly
- Ensure your PDF is text-based (not scanned images)
- Use clear section headers (Experience, Education, Skills)
- Keep formatting consistent

### Upload fails
- Check file size (must be under 16MB)
- Ensure file is actually a PDF
- Check folder permissions for uploads/

## Browser Compatibility

Works on:
- ✅ Chrome/Edge (90+)
- ✅ Firefox (88+)
- ✅ Safari (14+)
- ✅ Opera (76+)

## Performance

- Upload: < 1 second
- Processing: 2-5 seconds (depending on PDF complexity)
- Preview: Instant
- Download: Instant

## Security

- File size limits prevent DoS
- Secure filename handling
- No data persistence
- No external API calls
- All processing local

## Tips for Best Results

1. **Resume Formatting**
   - Use clear section headers
   - Keep consistent date formats
   - Put contact info at the top

2. **File Quality**
   - Use text-based PDFs (not scanned images)
   - Keep file size reasonable
   - Use standard fonts

3. **Content**
   - Include all relevant sections
   - Use bullet points for descriptions
   - Keep it concise and clear

## Future Enhancements

Potential additions:
- [ ] Multiple portfolio themes
- [ ] Custom color picker
- [ ] LinkedIn import
- [ ] Export to PDF
- [ ] Multi-language support
- [ ] GitHub integration
- [ ] Analytics integration

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your resume PDF is valid
3. Check browser console for errors
4. Try with the sample resume

## License

Free to use for personal and commercial projects.

---

**Made with ❤️ using Flask, Python, and modern web technologies**
