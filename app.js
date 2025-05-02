// backend/app.js
const express = require('express');
const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');
const { PDFDocument } = require('pdf-lib');
const twilio = require('twilio');
const bodyParser = require('body-parser');
const cors = require('cors');

// Twilio setup
const twilioSID = 'Q5VMOUAIEVKLA7PWJGNHUJL6';
const twilioAuth = 'lRIKd0DSwt8yi[xsjYO9Vg-u3UWmzoEr1MFqbhJ2NkGB';
const twilioFrom = '+1XXXXXXXXXX'; // your Twilio phone number
const twilioTo = '+12133255675';

const app = express();
app.use(cors());
app.use(bodyParser.json());

// PDF field order should match this list
const fieldOrder = [
  "Full Name", "Date of Birth", "Social Security Number", "Phone Number", "Email Address",
  "Home Address", "City, State, ZIP", "Employer Name", "Employer Address", "Job Title",
  "Start Date", "End Date (if applicable)", "Hourly Wage", "Hours per Week",
  "Schedule (Days/Times)", "Did you take lunch breaks?", "Were you paid for all hours worked?",
  "Were you reimbursed for expenses?", "Did you wear a uniform or use your own tools?",
  "Any additional details about your job or termination"
];

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'YOUR_EMAIL@gmail.com',
    pass: 'YOUR_EMAIL_PASSWORD'
  }
});

app.post('/submit-intake', async (req, res) => {
  try {
    const data = req.body;
    const pdfTemplate = fs.readFileSync(path.join(__dirname, 'intake_form_template.pdf'));
    const pdfDoc = await PDFDocument.load(pdfTemplate);
    const pages = pdfDoc.getPages();
    const firstPage = pages[0];
    const { width, height } = firstPage.getSize();

    const font = await pdfDoc.embedFont(PDFDocument.PDFName.of('Helvetica'));
    let y = height - 110;

    for (let key of fieldOrder) {
      const text = data[key] || '';
      firstPage.drawText(text, {
        x: 200,
        y: y,
        size: 10,
        font,
      });
      y -= 25;
    }

    const pdfBytes = await pdfDoc.save();
    const tempPath = path.join(__dirname, 'output.pdf');
    fs.writeFileSync(tempPath, pdfBytes);

    // Email with PDF attachment
    await transporter.sendMail({
      from: 'Tous Law Intake <YOUR_EMAIL@gmail.com>',
      to: ['dtous@touslaw.com', 'gbeilfuss@touslaw.com'],
      subject: `New Intake: ${data['Full Name']}`,
      text: `A new intake form has been submitted. Name: ${data['Full Name']}.`,
      attachments: [{ filename: 'IntakeForm.pdf', path: tempPath }]
    });

    // Send Twilio SMS
    const client = twilio(twilioSID, twilioAuth);
    await client.messages.create({
      body: `New Lead: ${data['Full Name']} — ${data['Any additional details about your job or termination']} — ${data['Phone Number']}`,
      from: twilioFrom,
      to: twilioTo
    });

    res.json({ success: true });
  } catch (err) {
    console.error('Error processing intake:', err);
    res.status(500).json({ error: 'Server error' });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🔥 Intake backend running on port ${PORT}`));
