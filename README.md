# LearnHub — Complete LMS (All 8 Phases ✅)

## ✅ Phase 1 — Authentication + Role-based Dashboards
- Custom User model with 3 roles: STUDENT, TEACHER, ADMIN
- Student signup (auto-activated) / Teacher signup (needs Admin approval)
- Role-based login → automatic redirect to the right dashboard
- Student / Teacher / Admin dashboards with basic stats

## ✅ Phase 2 — Course System
- **Public course browsing**: search + filter by category / free-paid, at `/courses/`
- **Course detail page**: accordion-style curriculum (sections → lessons), locked/unlocked based on enrollment or preview
- **Teacher: Create Course** — title, category, description, thumbnail, Free/Paid toggle, price
- **Teacher: Content Builder** — add unlimited Sections, and inside each Section add Lessons (Video file / Video URL / PDF notes), mark lessons as free "Preview"
- **Approval workflow**: every new/edited course goes to `PENDING` status; goes live only after Admin approves it from Django Admin
- Lesson viewer page (video player / PDF download link)

## ✅ Phase 3 — Course Progress Tracking (NEW)
- **Enroll for Free** — students can now actually enroll in free courses with one click (`Enroll for Free` button on course detail page); this creates a real `Enrollment` record
- **Mark as Complete** — every lesson page has a "Mark as Complete" button for enrolled students
- **Auto progress %** — `Enrollment.progress_percent` recalculates automatically (completed lessons ÷ total lessons) every time a lesson is marked complete
- **Visual feedback** — course detail page shows a progress bar + ✅ checkmarks next to completed lessons; student dashboard already displays this progress bar per course
- Paid-course purchase still needs Phase 4 (payment) — "Buy Now" is a placeholder until then

All phases tested end-to-end using Django's test client (course creation → section → lesson → enroll → mark complete → progress 0%→50%→100%) — fully working.

## ✅ Phase 4 — Payment (Razorpay) + Coupons (NEW)
- **Checkout page** for paid courses — shows price, lets student apply a coupon code before paying
- **Coupon system** — Admin creates coupons in Django Admin (code, % discount, validity dates, max uses); checkout auto-validates and applies the discount (e.g. `WELCOME20` → 20% off)
- **Razorpay integration** — "Pay Now" creates a real Razorpay Order via the Razorpay Python SDK and opens Razorpay's Checkout popup (`checkout.js`)
- **Signature verification** — after payment, Razorpay's response is verified server-side using HMAC signature verification (`client.utility.verify_payment_signature`) — this is the secure way to confirm a payment actually succeeded, never trust the frontend alone
- **Auto-unlock on success** — once verified, an `Order` is marked `PAID` and the student is automatically `Enrolled` in the course — no manual step needed
- **My Orders page** — students can see their order/payment history

### ⚠️ Important: Add your real Razorpay keys
This ships with placeholder test keys in `learnhub/settings.py`. To actually process payments:
1. Sign up at https://dashboard.razorpay.com and grab your **Test Mode** API Key ID + Secret
2. Set them as environment variables before running the server:
   ```bash
   export RAZORPAY_KEY_ID="rzp_test_yourkeyhere"
   export RAZORPAY_KEY_SECRET="yoursecrethere"
   ```
   (or edit the defaults directly in `settings.py` for local testing)
3. Use Razorpay's [test card numbers](https://razorpay.com/docs/payments/payments/test-card-upi-details/) to simulate a payment in Test Mode

The signature-verification logic itself has been tested and confirmed working correctly (verified with a simulated HMAC signature) — it will work exactly the same with real keys.

## ✅ Phase 5 — Online Test / MCQ System (NEW)
- **Teacher: Create Test** — set duration (minutes), pass percentage, optional negative marking (marks deducted per wrong answer), attempt limit, and optional question randomization
- **Teacher: Add MCQ Questions** — 4 options (A/B/C/D) + mark the correct one; unlimited questions per test
- **Teacher: Results overview** — see every student's score, percentage, pass/fail status per test
- **Student: Take Test** — countdown timer shown on screen, turns red in the last minute, **auto-submits** the form the instant time runs out
- **Auto-grading** — correct/wrong/unanswered counted automatically; negative marking subtracted if enabled; score never goes below 0
- **Instant result** — percentage + PASSED/FAILED shown right after submit, with a full answer review (your answer vs correct answer)
- **Attempt limit enforcement** — once a student uses up their allowed attempts, "Start Test" is disabled and direct URL access is blocked too
- **Result history** — students can see all their past attempts across a course's tests

Tested end-to-end: created a 4-question test → student answered 3/4 correct → got 75% → PASSED (pass mark was 50%). Also verified: attempt-limit blocking after 2 attempts, and negative marking correctly reducing score (and clamping at 0, never negative).

## ✅ Phase 6 — Live Classes / Zoom & Google Meet Integration (NEW)
- **Teacher: Schedule Live Class** — title, platform (Zoom / Google Meet / Other), meeting link, date & time, duration, optional notes/agenda
- **Teacher: Manage Live Classes** — edit or delete any scheduled class, see status (Upcoming / 🔴 LIVE / Ended) per course
- **Student: Course Live Classes tab** — enrolled students see Upcoming & Past classes for that course, with a "Join Live Class" button that opens the Zoom/Meet link in a new tab; automatically shows "🔴 LIVE NOW" while the class is actually in progress (based on scheduled time + duration)
- **Student: "My Live Classes"** — a single cross-course page showing every upcoming live class across all courses the student is enrolled in (handy as a personal live-class calendar)

This uses simple external meeting links (Zoom/Google Meet) rather than building custom video streaming — as recommended, this is the practical approach to start with. A custom live-streaming system (with chat, screen share, attendance, recording) would be a bigger future upgrade.

Tested end-to-end: teacher scheduled a class → showed as "Upcoming" for the student with the correct meeting link → a second class scheduled to start 10 minutes ago correctly showed "🔴 LIVE NOW" — status auto-calculates from the current time, no manual toggling needed.

## ✅ Phase 7 — Certificate Auto-Generation (NEW)
- **Auto-issue on 100% completion** — the moment a student's course progress hits 100% (i.e. every lesson marked complete), a `Certificate` record is created automatically — no manual step for teacher or admin
- **Real PDF generation** — uses `reportlab` to render an actual designed certificate PDF (navy/gold border, student name, course title, instructor name, issue date, unique verification code) — not just a text file
- **My Certificates page** — students see every certificate they've earned with a one-click PDF download
- **Public Certificate Verification** — anyone (e.g. an employer) can go to `/verify-certificate/` and enter the short verification code (e.g. `76EB73CB`) printed on the certificate to confirm it's genuine — shows student name, course, and issue date if valid

Tested end-to-end: enrolled a student in a 1-lesson course → marked that lesson complete → progress hit 100% → certificate auto-generated with a real PDF → downloaded successfully → verified via the public code lookup (both valid-code and invalid-code cases confirmed working). Certificate PDF was visually inspected and renders cleanly.

## ✅ Phase 8 — Production Deployment (NEW)
The app is now **environment-driven**: it runs with zero config for local development (SQLite, local media, DEBUG on), and automatically switches to production settings the moment you set environment variables — no code changes needed to go live.

- **PostgreSQL** — set `DATABASE_URL` and the app switches from SQLite automatically
- **Cloudinary media storage** — set `USE_CLOUDINARY=True` + credentials so uploaded videos/PDFs/certificates survive redeploys (critical: hosting platforms wipe local disk on every deploy)
- **Security hardening** — HTTPS redirect, secure cookies, HSTS headers all auto-enable when `DEBUG=False`
- **Whitenoise** — serves static files efficiently in production without needing a separate CDN
- **Deploy configs included** — `railway.json` (Railway) and `render.yaml` (Render), plus a `Procfile` and `runtime.txt` for other Heroku-style platforms
- **Full guide** — see `DEPLOYMENT.md` for step-by-step domain/SSL/environment-variable setup

Verified locally: `python manage.py check --deploy` → **0 issues** with `DEBUG=False` and a real secret key; `DATABASE_URL` correctly parses into a working PostgreSQL config; Cloudinary storage backend loads without errors; `collectstatic` successfully processed all 131 static files through Whitenoise; and all major pages (home, course list, login, certificate verification) still load correctly after the settings restructure.







## Setup (local machine par)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # Admin account banane ke liye
python manage.py runserver
```

Browser me kholiye: http://127.0.0.1:8000/

## Try karne ka flow

1. Superuser se `/admin/` me jaake ek **Category** bana dijiye (e.g. "Web Development")
2. `/signup/` se Teacher account banaiye, phir Admin se `/admin/` me us user ko `is_approved` = True karein
3. Teacher login karke `/teacher/courses/create/` se course banayein → phir "Manage Content" se Sections/Lessons add karein
4. Admin se `/admin/` → Courses me jaake naya course select karke "Approve selected courses" action chalayein
5. **Free course**: Student login karke "Enroll for Free" click kare, phir lessons kholke "Mark as Complete" click kare — progress bar automatically update hoga
6. **Paid course**: Admin ek Coupon bana sakte hain (`/admin/` → Coupons), phir student "Buy Now" → checkout page par coupon apply kare → "Pay with Razorpay" (real test keys chahiye — upar dekhein)
7. **Tests**: Teacher course builder se "Manage Tests" → test banayein → questions add karein. Enrolled student course detail se "Take Tests" → test attempt kare → turant result dekhe
8. **Live Classes**: Teacher course builder se "Live Classes" → schedule kare (Zoom/Meet link + date/time). Enrolled student course detail se "Live Classes" ya navbar se "Live Classes" (cross-course view) me dekh sakta hai, aur "Join" button se meeting khul jaati hai
9. **Certificates**: Jab student saare lessons ek course ke "Mark as Complete" kar deta hai (100% progress), certificate automatically ban jaata hai — navbar se "Certificates" me dekh/download kar sakta hai. Koi bhi navbar se "Verify Certificate" se certificate ka verification code daal ke check kar sakta hai
10. **Production deploy**: Jab live jaana ho, `DEPLOYMENT.md` follow karein — Railway ya Render par deploy, PostgreSQL attach, Cloudinary setup, environment variables set. Koi code change nahi chahiye, sirf environment variables.

## Project structure

```
learnhub/
├── accounts/       # User model, roles, signup/login
├── courses/        # Category, Course, Section, Lesson, Enrollment + full CRUD views/templates
├── payments/       # Order, Coupon models + Razorpay checkout flow
├── exams/          # Test, Question, Result models + teacher/student test flows
├── live_classes/   # LiveClass model + scheduling (Zoom/Meet links) + join flow
├── certificates/   # Certificate model + PDF generation (reportlab) + public verification
├── dashboard/      # Role-based dashboards
├── templates/
├── static/
├── DEPLOYMENT.md   # Full production deployment guide
├── .env.example    # Environment variables template
├── railway.json    # Railway deployment config
├── render.yaml     # Render deployment config
└── Procfile        # For other Heroku-style platforms
```

## 🎉 All 8 phases complete!

Aapka LearnHub LMS ab fully functional hai:
1. ✅ Authentication + role-based dashboards
2. ✅ Course system (create, browse, manage)
3. ✅ Course progress tracking
4. ✅ Payment (Razorpay) + coupons
5. ✅ Online test/MCQ system with timer
6. ✅ Live classes (Zoom/Meet)
7. ✅ Certificate auto-generation
8. ✅ Production deployment setup

Agar koi specific feature aur enhance karna ho (jaise: email notifications, student-to-teacher Q&A messaging, cart/multi-course checkout, custom video streaming, mobile app), bata dijiye — main us par kaam kar sakta hoon.

