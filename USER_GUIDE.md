# 📖 User Guide: Jotform to Airtable Sync

**Version 1.0**  
**Last Updated: February 2026**

---

## 🎯 Welcome!

This guide is designed for non-technical users who need to manage the Jotform to Airtable sync system. No programming knowledge is required to use this guide. We'll walk you through everything step-by-step using simple language and clear examples.

---

## 📋 Table of Contents

1. [What Does This Tool Do?](#what-does-this-tool-do)
2. [Automatic vs Manual Operations](#automatic-vs-manual-operations)
3. [Understanding Your Airtable Columns](#understanding-your-airtable-columns)
4. [Step-by-Step Instructions](#step-by-step-instructions)
   - [Making New Fields Visible (Unhiding)](#making-new-fields-visible-unhiding)
   - [Deleting Fields](#deleting-fields)
   - [Renaming Fields](#renaming-fields)
   - [Running a Manual Sync](#running-a-manual-sync)
   - [Checking Sync Status](#checking-sync-status)
5. [Troubleshooting Common Issues](#troubleshooting-common-issues)
6. [How to Get Help](#how-to-get-help)

---

## 🌟 What Does This Tool Do?

Think of this tool as a **bridge** between your Jotform (where people submit information) and your Airtable (where you manage and organize that information).

### In Simple Terms:

- **You collect data** through a Jotform form
- **People submit responses** via the form
- **This tool automatically copies** those responses to Airtable
- **You can then view, sort, and analyze** the data in Airtable

### Key Benefits:

✅ **Automatic syncing** - No manual copy-pasting needed  
✅ **Real-time updates** - New submissions appear in Airtable automatically  
✅ **Two-way field management** - Add questions to Jotform, and columns appear in Airtable  
✅ **Reliable tracking** - Every submission is tracked by a unique ID

---

## ⚡ Automatic vs Manual Operations

Understanding what happens automatically vs what requires your action is crucial!

### 🤖 Automatic Operations (No Action Needed)

These happen automatically every hour:

| What Happens | Description | Your Action |
|--------------|-------------|-------------|
| 📥 **New Submissions** | Someone fills out the Jotform | None - just check Airtable |
| 🔄 **Updated Submissions** | Someone updates their response | None - changes sync automatically |
| ➕ **New Fields Created** | You add a question to Jotform | ⚠️ Unhide the column in Airtable |

> **⏰ Sync Schedule:** The automatic sync runs every hour, on the hour (1:00 PM, 2:00 PM, etc.)

### 👤 Manual Operations (You Need to Act)

These require you to take action in both Jotform AND Airtable:

| What You Do | Where | Manual Steps Required |
|-------------|-------|----------------------|
| ❌ **Delete a Question** | Jotform | Must manually delete column in Airtable too |
| ✏️ **Rename a Question** | Jotform | Must manually rename column in Airtable too |
| 👁️ **See New Columns** | Airtable | Must unhide newly created columns |

> **⚠️ Important:** The tool cannot automatically delete or rename Airtable columns due to Airtable's safety restrictions. This protects your data from accidental changes!

---

## 📊 Understanding Your Airtable Columns

When you open your Airtable base, you'll see several columns. Here's what the key columns mean:

### Essential Columns:

| Column Name | What It Is | Why It's Important |
|-------------|------------|-------------------|
| **Submission ID** | Unique identifier for each form submission | Used to track and update submissions - DO NOT DELETE |
| **Name (First)** | Person's first name | Split automatically from full name field |
| **Name (Last)** | Person's last name | Split automatically from full name field |
| **Email** | Person's email address | Contact information |

### Address Fields:

Complex fields like addresses are automatically split into separate columns:

- **Home Address (Street)**
- **Home Address (Street Line 2)**
- **Home Address (City)**
- **Home Address (State/Province)**
- **Home Address (Postal/Zip Code)**

The same applies to Business Addresses.

### Phone Number Fields:

- **Personal Phone Number** - Full phone number with area code
- **Business Phone Number** - Full business phone number

> **💡 Tip:** The tool automatically formats phone numbers for consistency.

---

## 📝 Step-by-Step Instructions

### Making New Fields Visible (Unhiding)

When you add a new question to your Jotform, the tool automatically creates a matching column in Airtable. However, **Airtable hides new columns by default** (this is an Airtable limitation, not something we can control).

#### Follow These Steps:

1. **Open Your Airtable Base**
   - Go to airtable.com
   - Sign in to your account
   - Click on your base (database)

2. **Look for Hidden Fields**
   - Scroll all the way to the right in your table
   - Look for either:
     - A **"+"** button at the end of your columns
     - A **"Hidden fields"** link or icon
   
3. **Click to View Hidden Fields**
   - Click on "Hidden fields" or the "+" button
   - You'll see a dropdown menu showing all hidden columns

4. **Unhide the Column You Want**
   - Find the field name in the list
   - Click the **eye icon** 👁️ next to the field name
   - The column will now appear in your table!

5. **Reorder the Column (Optional)**
   - Click and drag the column header to move it
   - Place it wherever makes sense for your workflow

#### 📸 What You Should See:

- Before: Empty "+ " or "Hidden fields" indicator
- During: List of hidden fields with eye icons
- After: New column visible in your table

#### ⏱️ When to Do This:

Do this **after adding a new question** to your Jotform and **after the next hourly sync runs**. Usually within 1-2 hours of adding the question.

---

### Deleting Fields

If you remove a question from your Jotform, you need to manually delete the corresponding column in Airtable.

> **⚠️ Warning:** Deleting a column permanently removes all data in that column. Make sure you really want to delete it!

#### Part 1: Delete from Jotform

1. **Go to Your Jotform**
   - Open jotform.com
   - Sign in to your account
   - Go to "My Forms"

2. **Edit Your Form**
   - Find the form you're using for this sync
   - Click "Edit Form"

3. **Delete the Question**
   - Find the question you want to remove
   - Click on it to select it
   - Click the trash/delete icon or right-click and select "Delete"
   - Click "Save" at the top right

#### Part 2: Delete from Airtable

1. **Open Your Airtable Base**
   - Go to airtable.com
   - Open your base

2. **Find the Column to Delete**
   - Locate the column that matches the question you deleted
   - Make sure it's the right one!

3. **Delete the Column**
   - Click the **dropdown arrow** in the column header (▼)
   - Scroll down and click **"Delete field"**
   - Airtable will ask you to confirm
   - Type the field name to confirm (safety feature)
   - Click **"Delete field"** to confirm

4. **Verify It's Gone**
   - The column should disappear from your table
   - All data in that column is now permanently deleted

#### ⚡ Important Notes:

- ❌ The sync tool **cannot** delete Airtable columns automatically
- 🛡️ This is a safety feature to prevent accidental data loss
- 💾 If you want to keep the data, export it first before deleting

---

### Renaming Fields

If you rename a question in your Jotform, you need to manually rename the corresponding column in Airtable.

> **📌 Note:** This is a manual process. The tool cannot automatically rename columns in Airtable.

#### Part 1: Rename in Jotform

1. **Open Your Jotform Form**
   - Go to jotform.com
   - Sign in and go to "My Forms"
   - Click "Edit Form" on your form

2. **Edit the Question**
   - Click on the question you want to rename
   - Change the question text/label
   - Click "Save" at the top right

#### Part 2: Rename in Airtable

1. **Open Your Airtable Base**
   - Go to airtable.com
   - Open your base

2. **Find the Column to Rename**
   - Locate the column with the old name
   - Make sure it's the correct column!

3. **Rename the Column**
   - Click the **dropdown arrow** in the column header (▼)
   - Click **"Customize field type"**
   - In the popup that appears:
     - Find the **"Name"** field at the top
     - Change it to match your new Jotform question name
     - Click **"Save"** at the bottom

4. **Verify the Change**
   - The column header should now show the new name
   - All existing data remains intact

#### 🎯 Best Practice:

Try to finalize your form question names before going live. This reduces the need for renaming later!

---

### Running a Manual Sync

Normally, the sync runs automatically every hour. But sometimes you might want to run it immediately:

- ✅ You just added a new question and want to see the column now
- ✅ You're testing the system
- ✅ You know there are new submissions and want them in Airtable ASAP
- ✅ You're troubleshooting an issue

#### Follow These Steps:

1. **Go to GitHub**
   - Open your web browser
   - Go to: `github.com/OluwaseyiFad/airtable-jotform-sync`
   - Make sure you're signed in

2. **Click on "Actions" Tab**
   - At the top of the page, you'll see tabs: Code, Issues, Pull requests, **Actions**
   - Click **Actions**

3. **Find the Workflow**
   - On the left sidebar, you'll see "Sync Jotform to Airtable"
   - Click on it

4. **Run the Workflow**
   - On the right side, you'll see a **"Run workflow"** button
   - Click **"Run workflow"**
   - A small menu appears
   - Click the green **"Run workflow"** button again

5. **Wait for Completion**
   - The workflow will start running
   - You'll see a yellow circle 🟡 (running) or rotating icon
   - Wait 1-3 minutes
   - When done, you'll see either:
     - Green checkmark ✅ (success)
     - Red X ❌ (error)

6. **Check Airtable**
   - Go to your Airtable base
   - Refresh the page
   - New submissions should now be visible!

#### ⏱️ How Long Does It Take?

- Usually **1-3 minutes**
- Depends on how many new/updated submissions there are
- You can watch the progress in real-time

---

### Checking Sync Status

Want to know if the sync is working? Here's how to check:

#### Method 1: GitHub Actions Tab

1. **Go to GitHub Actions**
   - Navigate to: `github.com/OluwaseyiFad/airtable-jotform-sync`
   - Click the **Actions** tab

2. **Look at Recent Runs**
   - You'll see a list of recent sync runs
   - Each row shows:
     - 🟢 Green checkmark = Success
     - 🔴 Red X = Error/Failed
     - 🟡 Yellow circle = Currently running
     - The date and time of the run

3. **Click on a Run for Details**
   - Click on any run to see details
   - You'll see:
     - How many submissions were processed
     - How long it took
     - Any errors that occurred

#### Method 2: Check Watermark File

The system keeps track of the last sync time in a file called `watermark.json`:

1. **Go to GitHub Repository**
   - Click **Code** tab
   - Find and click `watermark.json` in the file list

2. **Check the Timestamp**
   - You'll see something like: `{"last_updated_at": 1737331200}`
   - This is a Unix timestamp (seconds since 1970)
   - If it's recent, the sync is working!

> **💡 Tip:** If you see the timestamp updating every hour, the automatic sync is working perfectly!

#### Method 3: Check Airtable Directly

1. **Open Airtable**
   - Go to your base
   - Look at the most recent entries

2. **Look for New Submissions**
   - Sort by **Submission ID** (descending)
   - Or sort by a date field
   - Recent submissions should appear within an hour of being submitted

#### 🚦 What's Normal?

✅ **Green checkmarks** in Actions tab every hour  
✅ **Watermark updates** hourly  
✅ **New submissions appear** within 1 hour in Airtable  
✅ **Updated submissions refresh** within 1 hour

---

## 🆘 Troubleshooting Common Issues

### Issue 1: New Column Not Showing Up in Airtable

**Symptoms:**
- You added a question to Jotform
- The sync ran successfully (green checkmark)
- But you don't see the column in Airtable

**Solution:**
The column is probably hidden! Follow the [Making New Fields Visible](#making-new-fields-visible-unhiding) instructions above.

**Why This Happens:**
Airtable automatically hides new columns created via the API. This is an Airtable limitation, not a bug in our tool.

---

### Issue 2: Sync Shows Red X (Failed)

**Symptoms:**
- In the Actions tab, you see a red X ❌
- The sync didn't complete

**Solution Steps:**

1. **Click on the Failed Run**
   - Click on the red X run in the Actions tab
   - Click on the "sync" job

2. **Read the Error Message**
   - Look for red error text
   - Common errors include:
     - "Missing required config" = API keys might be wrong
     - "401 Unauthorized" = Check API credentials
     - "Invalid value for column" = Data type mismatch

3. **Contact Technical Support**
   - Note down the error message
   - Note down the time it happened
   - Reach out to your technical contact (see [How to Get Help](#how-to-get-help))

**Common Causes:**
- ❌ API keys expired or invalid
- ❌ Internet connectivity issue
- ❌ Jotform or Airtable service temporarily down
- ❌ Data type mismatch between Jotform and Airtable

---

### Issue 3: Data Looks Wrong in Airtable

**Symptoms:**
- Data appears in Airtable but looks incorrect
- Numbers show up as text
- Dates are formatted oddly
- Multi-select fields don't work

**Solution:**

1. **Check the Original Submission**
   - Go to Jotform
   - Find the submission in question
   - Verify what the original data looks like

2. **Check the Field Type**
   - In Airtable, check the column type
   - Click dropdown arrow → "Customize field type"
   - Make sure the type matches the data (Number, Date, Text, etc.)

3. **Run a Manual Sync**
   - Sometimes re-syncing fixes the issue
   - Follow [Running a Manual Sync](#running-a-manual-sync) instructions

**If Still Wrong:**
- The field might need special handling in the code
- Contact technical support with specific examples

---

### Issue 4: Sync Hasn't Run in Hours

**Symptoms:**
- Last successful sync was more than 2 hours ago
- No recent runs in Actions tab

**Solution Steps:**

1. **Check GitHub Status**
   - Go to: githubstatus.com
   - See if GitHub Actions is having issues

2. **Run a Manual Sync**
   - Follow [Running a Manual Sync](#running-a-manual-sync) instructions
   - If it works, the automatic schedule might have paused

3. **Check Repository Settings**
   - This might require technical assistance
   - Make sure Actions are enabled
   - Make sure the repository hasn't been archived

**When to Worry:**
- ⚠️ If manual sync also fails
- ⚠️ If no runs appear after 24 hours
- ⚠️ Contact technical support immediately

---

### Issue 5: Can't Access the GitHub Repository

**Symptoms:**
- "404 Not Found" error
- "You don't have access" message

**Solution:**

1. **Check Your Email**
   - Look for an invitation email from GitHub
   - Click "Accept Invitation" in the email

2. **Make Sure You're Logged In**
   - Go to github.com
   - Click "Sign in" in the top right
   - Enter your credentials

3. **Contact the Repository Owner**
   - They may need to resend the invitation
   - Or add you as a collaborator

**See Also:**
[GITHUB_ACCESS_GUIDE.md](GITHUB_ACCESS_GUIDE.md) for detailed GitHub access instructions.

---

### Issue 6: Duplicate Entries in Airtable

**Symptoms:**
- Same submission appears multiple times
- Duplicate rows for the same person

**Why This Happens:**
This should NOT happen because the system tracks submissions by Submission ID. If you see duplicates:

1. **Check Submission IDs**
   - Look at the "Submission ID" column
   - Are they the same or different?

2. **If IDs Are Different:**
   - These might be legitimate separate submissions
   - The person submitted the form multiple times

3. **If IDs Are the Same:**
   - This is a bug - contact technical support immediately
   - Include the Submission ID in your report

---

### Issue 7: Missing Data in Some Fields

**Symptoms:**
- Some fields are blank in Airtable
- But they have data in Jotform

**Common Causes:**

1. **Field is Skipped Intentionally**
   - Some fields are configured to be skipped
   - Examples: "Business Phone Number (Area Code)" when full number exists
   - This is normal behavior

2. **Field Type Mismatch**
   - Data might not convert properly
   - Example: Text in a number field

3. **New Field Not Yet Synced**
   - If you just added the field, wait for next sync
   - Or run a manual sync

**Solution:**
- Check if the field is in the SKIP_FIELDS list (ask technical support)
- Verify data types match
- Run a manual sync

---

### Issue 8: Vocational Fields Show Wrong Values

**Symptoms:**
- Fields like "1. Public Health/Hospitals" show odd values

**Solution:**
These fields have special formatting rules:
- "0-2 years" becomes "0-2 Years"
- "> 10 years" becomes "> 10 Years"

This is intentional for consistency. If you see other weird values, contact support.

---

## 🆘 How to Get Help

### Before Reaching Out:

✅ Check this guide first  
✅ Look at the [Troubleshooting](#troubleshooting-common-issues) section  
✅ Check the [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for quick answers

### When You Need Help:

**Gather This Information:**

1. **What were you trying to do?**
   - Example: "I was trying to unhide a new field"

2. **What happened instead?**
   - Example: "The field doesn't appear in the hidden fields list"

3. **When did it happen?**
   - Date and time
   - Example: "February 18, 2026 at 2:30 PM"

4. **Any error messages?**
   - Take a screenshot
   - Or copy and paste the exact error text

5. **What have you tried already?**
   - Example: "I ran a manual sync, but it didn't help"

### Contact Information:

**For Technical Issues:**
- Email: [Your technical support email]
- Phone: [Your support phone number]
- Response time: Usually within 24 hours

**For GitHub Access Issues:**
- Repository Owner: OluwaseyiFad
- GitHub Support: support@github.com

**For Urgent Issues:**
- [Your urgent contact method]
- Define what counts as urgent (e.g., sync completely broken, data loss)

---

## 📚 Additional Resources

### Related Documentation:

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page cheat sheet
- **[GITHUB_ACCESS_GUIDE.md](GITHUB_ACCESS_GUIDE.md)** - Complete GitHub setup guide
- **[TECHNICAL_SETUP_GUIDE.md](TECHNICAL_SETUP_GUIDE.md)** - For technical users and developers
- **[VIDEO_RECORDING_SCRIPT.md](VIDEO_RECORDING_SCRIPT.md)** - Video tutorial scripts

### Video Tutorials:

(Videos to be added soon!)

1. **Overview & Introduction** (5-7 min) - [Coming Soon]
2. **Making New Fields Visible** (3-4 min) - [Coming Soon]
3. **Deleting and Renaming Fields** (5-6 min) - [Coming Soon]
4. **Running Manual Sync & Checking Status** (4-5 min) - [Coming Soon]
5. **Troubleshooting Common Issues** (6-8 min) - [Coming Soon]

### External Resources:

- **Airtable Help:** support.airtable.com
- **Jotform Help:** jotform.com/help
- **GitHub Docs:** docs.github.com

---

## 🎓 Quick Tips for Success

### Daily Tasks:

✅ Check Airtable once a day for new submissions  
✅ Monitor the Actions tab once a week for red X's  
✅ Keep your GitHub password secure

### Weekly Tasks:

✅ Review any new fields that need unhiding  
✅ Check that sync is running on schedule  
✅ Clean up any test submissions

### Monthly Tasks:

✅ Review your Airtable structure  
✅ Archive old data if needed  
✅ Update this documentation if processes change

---

## 💡 Frequently Asked Questions

**Q: How often does the sync run?**  
A: Automatically every hour, on the hour (1:00, 2:00, 3:00, etc.). You can also run it manually anytime.

**Q: What happens if someone updates their submission?**  
A: The sync will update the existing record in Airtable with the new information.

**Q: Can I pause the automatic sync?**  
A: Yes, but this requires technical knowledge. Contact your technical support team.

**Q: Will I lose data if I delete a field?**  
A: Yes! Deleting a column in Airtable permanently deletes all data in that column. Make sure to export it first if you need to keep it.

**Q: Why are new columns hidden?**  
A: This is an Airtable API limitation. Airtable hides all new columns created programmatically to prevent accidental display of unreviewed data.

**Q: Can I change the sync schedule?**  
A: Yes, but it requires editing the GitHub workflow file. Contact your technical support team.

**Q: What's a "Submission ID"?**  
A: It's a unique identifier assigned by Jotform to every form submission. It's how the system tracks which submission is which.

**Q: Can I use this with multiple forms?**  
A: Not simultaneously. The system is configured for one form at a time. To switch forms, you need to update the configuration (requires technical knowledge).

---

## ✅ Summary Checklist

Use this checklist to make sure you understand the basics:

- [ ] I know what the tool does (syncs Jotform to Airtable)
- [ ] I understand automatic vs manual operations
- [ ] I know how to unhide new fields in Airtable
- [ ] I know how to delete fields from both platforms
- [ ] I know how to rename fields in both platforms
- [ ] I can run a manual sync via GitHub Actions
- [ ] I can check the sync status
- [ ] I know where to find troubleshooting help
- [ ] I know how to contact support if I need help
- [ ] I have bookmarked this guide for easy access

---

**End of User Guide**

*This guide was created with ❤️ for non-technical users. If you have suggestions for improving this guide, please share them with your technical team!*

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Repository:** github.com/OluwaseyiFad/airtable-jotform-sync
