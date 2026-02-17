# Frontend Testing Guide

## 🚀 How to Test Your Docusaurus Frontend

### Prerequisites
- Node.js (v20+) installed ✅
- npm installed ✅

### Method 1: Development Server Testing

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Start development server:**
```bash
cd frontend
npm start
```

3. **Test the frontend:**
- Open http://localhost:3000 in your browser
- Check that the site loads properly
- Navigate through the documentation pages
- Test the AI Chat page (/ai-chat)

### Method 2: Build Testing

1. **Build for production:**
```bash
cd frontend
npm run build
```

2. **Serve the built site:**
```bash
cd frontend
npm run serve
```

3. **Test the production build:**
- Open http://localhost:3000 in your browser
- Verify all pages work correctly

### Method 3: Automated Testing Script

Run the comprehensive frontend test:

```bash
cd frontend
node test_frontend.js
```

### Frontend Features to Test

#### 📚 Documentation Pages
- [ ] Homepage loads correctly
- [ ] Navigation menu works
- [ ] Sidebar navigation functions
- [ ] All documentation pages render
- [ ] Search functionality (if enabled)

#### 🤖 AI Chat Feature
- [ ] AI Chat page loads (/ai-chat)
- [ ] Chat interface displays
- [ ] Can send messages
- [ ] Receives responses from backend
- [ ] Citations display properly
- [ ] Error handling works

#### 🎨 UI Components
- [ ] Floating AI button appears on scroll
- [ ] Responsive design works on mobile
- [ ] Dark/light mode toggle (if enabled)
- [ ] Footer and navbar display correctly

#### 🔗 Backend Integration
- [ ] API calls to backend work
- [ ] Error handling for failed requests
- [ ] Loading states display properly

### Backend Connection Testing

The frontend connects to the backend at:
- **Production:** `https://farooquemalik50871-AI-Book-Backend.hf.space`
- **Local Development:** `http://localhost:8000` (when running backend locally)

To test with local backend:
1. Update `docusaurus.config.ts`:
```typescript
customFields: {
  backendUrl: 'http://localhost:8000',
}
```

2. Start both frontend and backend servers
3. Test AI chat functionality

### Troubleshooting

#### Build Errors
```bash
# Clear cache and rebuild
npm run clear
npm install
npm run build
```

#### Port Conflicts
- Frontend runs on port 3000 by default
- If port 3000 is busy, Docusaurus will use the next available port

#### API Connection Issues
- Check that backend is running
- Verify backend URL in `docusaurus.config.ts`
- Check browser console for CORS errors

#### TypeScript Errors
```bash
# Check types
npm run typecheck
```

### Performance Testing

1. **Lighthouse Audit:**
   - Open Chrome DevTools
   - Go to Lighthouse tab
   - Run performance audit

2. **Bundle Analysis:**
```bash
npm run build
# Check build/static/js for bundle sizes
```

### Cross-Browser Testing

Test on:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

### Accessibility Testing

- [ ] Keyboard navigation works
- [ ] Screen reader compatibility
- [ ] Color contrast is adequate
- [ ] Alt text on images

### Deployment Testing

1. **Vercel Deployment:**
```bash
npm run deploy
```

2. **Docker Build:**
```bash
docker build -t frontend .
docker run -p 3000:80 frontend
```