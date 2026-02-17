#!/usr/bin/env node

/**
 * Frontend Testing Script
 * Tests basic functionality of the Docusaurus site
 */

const http = require('http');

console.log('🧪 Testing Frontend...\n');

// Test if the development server is running
function testServer() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:3000', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('✅ Frontend server is running on http://localhost:3000');
          console.log('✅ Homepage loads successfully');

          // Check if it's a Docusaurus site
          if (data.includes('docusaurus')) {
            console.log('✅ Docusaurus site detected');
          }

          // Check for AI chat link
          if (data.includes('/ai-chat')) {
            console.log('✅ AI Chat page link found');
          }

          resolve(true);
        } else {
          console.log(`❌ Server responded with status: ${res.statusCode}`);
          resolve(false);
        }
      });
    });

    req.on('error', (err) => {
      console.log('❌ Frontend server is not running');
      console.log('💡 Start it with: cd frontend && npm start');
      resolve(false);
    });

    req.setTimeout(5000, () => {
      console.log('❌ Connection timeout - server may not be running');
      req.destroy();
      resolve(false);
    });
  });
}

// Test AI chat page
function testAIChatPage() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://localhost:3000/ai-chat', (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          console.log('✅ AI Chat page loads successfully');

          // Check for chat interface elements
          if (data.includes('AI Assistant') || data.includes('chat')) {
            console.log('✅ Chat interface elements found');
          }

          resolve(true);
        } else {
          console.log(`❌ AI Chat page failed with status: ${res.statusCode}`);
          resolve(false);
        }
      });
    });

    req.on('error', (err) => {
      console.log('❌ AI Chat page not accessible');
      resolve(false);
    });

    req.setTimeout(5000, () => {
      console.log('❌ AI Chat page timeout');
      req.destroy();
      resolve(false);
    });
  });
}

// Test API connectivity (if backend is running)
function testBackendConnection() {
  return new Promise((resolve, reject) => {
    // Test local backend first
    const req = http.request({
      hostname: 'localhost',
      port: 8000,
      path: '/health',
      method: 'GET'
    }, (res) => {
      if (res.statusCode === 200) {
        console.log('✅ Local backend is running on port 8000');
      } else {
        console.log('⚠️  Local backend not responding, will use production API');
      }
      resolve(true);
    });

    req.on('error', (err) => {
      console.log('⚠️  Local backend not running, frontend will use production API');
      resolve(false);
    });

    req.setTimeout(3000, () => {
      console.log('⚠️  Local backend connection timeout');
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

// Main test function
async function runTests() {
  console.log('1. Testing frontend server...');
  const serverRunning = await testServer();

  if (serverRunning) {
    console.log('\n2. Testing AI Chat page...');
    await testAIChatPage();
  }

  console.log('\n3. Checking backend connectivity...');
  await testBackendConnection();

  console.log('\n🎉 Frontend testing completed!');
  console.log('\n📋 Manual Testing Checklist:');
  console.log('- [ ] Open http://localhost:3000 in browser');
  console.log('- [ ] Navigate through documentation pages');
  console.log('- [ ] Test AI Chat functionality');
  console.log('- [ ] Check responsive design on mobile');
  console.log('- [ ] Verify all links work');

  if (!serverRunning) {
    console.log('\n🚀 To start the frontend server:');
    console.log('   cd frontend');
    console.log('   npm install');
    console.log('   npm start');
  }
}

runTests().catch(console.error);