# 🚀 HEROKU DASHBOARD DEPLOYMENT GUIDE
# For accounts with MFA enabled

## STEP 1: Push to GitHub First

1. Create a new repository on GitHub:
   - Go to github.com
   - Click "New repository"
   - Name: mini-100prosim
   - Make it Public
   - Don't initialize with README

2. Add GitHub as remote and push:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/mini-100prosim.git
   git branch -M main
   git push -u origin main
   ```

## STEP 2: Deploy via Heroku Dashboard

1. Go to: https://dashboard.heroku.com/
2. Click "New" → "Create new app"
3. App name: mini-100prosim-energy (or any available name)
4. Choose region: United States
5. Click "Create app"

## STEP 3: Connect to GitHub

1. In your new app dashboard, go to "Deploy" tab
2. Under "Deployment method", click "GitHub"
3. Search for your repository: mini-100prosim
4. Click "Connect"

## STEP 4: Set Environment Variables

1. Go to "Settings" tab
2. Click "Reveal Config Vars"
3. Add these variables:
   - SECRET_KEY: django-insecure-y#77%399dcbrd0jmnw#!60bl=f-iibe)=_kh-lklf=m_ptjn$)
   - DEBUG: False
   - ALLOWED_HOSTS: your-app-name.herokuapp.com

## STEP 5: Deploy

1. Go back to "Deploy" tab
2. Scroll down to "Manual deploy"
3. Select branch: main
4. Click "Deploy Branch"

## STEP 6: Open Your App

1. Click "Open app" button
2. Your Mini-100ProSim will be live!

---

## Alternative: Use Git to Deploy Directly

If you want to continue with command line, you need to:
1. Generate a Heroku API token
2. Use that token instead of password

But the Dashboard method above is much easier for MFA accounts!
