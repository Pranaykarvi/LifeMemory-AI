/**
 * Setup script to create .env.local file
 * Run: node setup-env.js
 */

const fs = require('fs');
const path = require('path');

const envContent = `# Frontend Environment Variables
# Generated automatically - do not edit manually

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://brcfzyyvgotqvgjwqkov.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJyY2Z6eXl2Z290cXZnandxa292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg2Mjk3NTcsImV4cCI6MjA4NDIwNTc1N30.XBF0XtzTm4k40az4dzM4-0Uu1ehXDduwkEhdQODVuh4

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
`;

const envPath = path.join(__dirname, '.env.local');

if (fs.existsSync(envPath)) {
  console.log('✅ .env.local already exists');
  console.log('   If you need to update it, edit it manually or delete and run this script again');
} else {
  fs.writeFileSync(envPath, envContent, 'utf8');
  console.log('✅ Created .env.local file');
  console.log('   Frontend environment variables are now configured');
}

console.log('\n📝 Next steps:');
console.log('   1. Make sure backend is running: cd ../backend && python main.py');
console.log('   2. Start frontend: npm run dev');
console.log('   3. Open http://localhost:3000 in your browser\n');

