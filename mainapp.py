from flask import Flask, render_template, request, redirect, url_for, send_file, session
from openai import OpenAI
from xhtml2pdf import pisa
from io import BytesIO

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # required for session handling

# Groq AI API
api_key = "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"
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subject = request.form['subject']
        time = request.form['time']
        days = request.form['days']
        syllabus = request.form['syllabus']

        prompt = (
            f"Generate a human-readable and well-structured {days}-day study plan "
            f"for the subject: {subject}. Assume {time} hours of study per day. "
            f"Make sure to distribute the following syllabus/topics across the days: {syllabus}. "
            f"Format the response with clear Day headings and bullet points for topics/tasks."
        )

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        plan = response.choices[0].message.content
        session['generated_plan'] = plan
        return redirect(url_for('plan'))
    return render_template('index.html')

@app.route('/plan')
def plan():
    plan = session.get('generated_plan', None)
    if not plan:
        return redirect(url_for('index'))
    return render_template('plan.html', plan=plan)

@app.route('/download')
def download_pdf():
    plan = session.get('generated_plan', None)
    if not plan:
        return redirect(url_for('index'))

    pdf_buffer = BytesIO()
    html = render_template('pdf_template.html', plan=plan)
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        return "Error creating PDF", 500

    pdf_buffer.seek(0)
    return send_file(pdf_buffer, download_name="study_plan.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
