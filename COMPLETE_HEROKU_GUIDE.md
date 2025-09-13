# 🔄 COMPLETE HEROKU ACCOUNT CHANGE & DEPLOYMENT GUIDE

## STEP 1: Login to Your New/Different Heroku Account
1. Open browser: https://dashboard.heroku.com/
2. Logout if currently logged in (click profile → Logout)
3. Login with your new/different Heroku account credentials
4. Complete MFA if prompted

## STEP 2: Create New App on Heroku
1. Click "New" → "Create new app"
2. App name: mini-100prosim-platform (choose any available name)
3. Region: United States
4. Click "Create app"

## STEP 3: Connect to Your GitHub Repository
1. In the app dashboard, go to "Deploy" tab
2. Under "Deployment method", select "GitHub"
3. Click "Connect to GitHub" (authorize if needed)
4. Search for repository: mini-100prosim
5. Click "Connect" next to deepti1999/mini-100prosim

## STEP 4: Set Environment Variables
1. Go to "Settings" tab
2. Click "Reveal Config Vars"
3. Add these 3 variables:

   KEY: SECRET_KEY
   VALUE: django-insecure-y#77%399dcbrd0jmnw#!60bl=f-iibe)=_kh-lklf=m_ptjn$)

   KEY: DEBUG
   VALUE: False

   KEY: ALLOWED_HOSTS
   VALUE: your-app-name.herokuapp.com
   (Replace 'your-app-name' with actual app name you chose)

## STEP 5: Deploy Your App
1. Go back to "Deploy" tab
2. Scroll to "Manual deploy" section
3. Branch: main
4. Click "Deploy Branch"

## STEP 6: Monitor Build Process
Heroku will:
- Install Python 3.9.19
- Install Django, OEMOF, and all dependencies
- Start your app with Gunicorn

## STEP 7: Open Your Live App
1. Once build is complete, click "Open app"
2. Your Mini-100ProSim will be live!

---

## ALTERNATIVE: Command Line with API Token (Advanced)

If you want to use command line:
1. Go to https://dashboard.heroku.com/account
2. Scroll to "API Key" section
3. Click "Regenerate API Key"
4. Copy the key
5. Run: heroku auth:token
6. Paste the API key when prompted

But the Dashboard method above is much easier!
