from flask import Flask, request, render_template_string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import re

app = Flask(__name__)

# ---------------- CLEAN TEXT ----------------
def clean_text(text):
    text = text.lower()
    return re.sub(r'[^a-z\s]', '', text)

# ---------------- DATASET ----------------
emails = [
    "Win money now", "Free prize available", "Claim reward now",
    "Limited offer click now", "Earn money fast",
    "Click to claim lottery",

    "Your bank account blocked login now",
    "Verify password immediately",
    "Reset your account now",
    "Update credit card details",
    "Suspicious login detected",

    "Hello how are you", "Meeting tomorrow",
    "Project discussion scheduled",
    "Lunch at 1pm", "Call me later",
    "Your order delivered", "Assignment due tomorrow"
]

labels = [
    1,1,1,1,1,1,   # spam
    2,2,2,2,2,     # malicious
    0,0,0,0,0,0,0  # safe
]

emails = [clean_text(e) for e in emails]

vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(emails)

X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2)

model = MultinomialNB()
model.fit(X_train, y_train)

accuracy = round(accuracy_score(y_test, model.predict(X_test))*100,2)

# ---------------- EXTRA ANALYSIS ----------------
def analyze_security_features(text):
    text_lower = text.lower()

    suspicious_keywords = ["bank", "password", "credit", "verify", "login"]
    urgency_words = ["urgent", "now", "immediately", "act fast"]
    links = re.findall(r'http[s]?://\S+|www\.\S+', text)

    keyword_score = sum(word in text_lower for word in suspicious_keywords)
    urgency_score = sum(word in text_lower for word in urgency_words)
    link_score = len(links)

    length = len(text.split())

    threat_score = (keyword_score*20 + urgency_score*15 + link_score*25)

    return {
        "keywords": keyword_score,
        "urgency": urgency_score,
        "links": link_score,
        "length": length,
        "threat_score": min(threat_score,100)
    }

# ---------------- UI ----------------
html = """
<!DOCTYPE html>
<html>
<head>
<title>AI Cyber Security Analyzer</title>
<style>
body{
    font-family: Arial;
    background:#020617;
    color:white;
    text-align:center;
    padding:40px;
}

.container{
    background:#0f172a;
    padding:30px;
    border-radius:20px;
    width:550px;
    margin:auto;
    box-shadow:0 0 50px rgba(0,255,255,0.2);
}

textarea{
    width:100%;
    height:120px;
    border-radius:10px;
    padding:10px;
}

button{
    margin-top:15px;
    padding:12px 25px;
    background:#06b6d4;
    border:none;
    border-radius:10px;
    color:white;
    cursor:pointer;
}

.bar{
    background:#1e293b;
    height:10px;
    border-radius:10px;
    margin-top:5px;
}

.fill{
    height:100%;
    border-radius:10px;
}

.section{
    text-align:left;
    margin-top:15px;
}

.safe{color:#22c55e;}
.spam{color:#facc15;}
.mal{color:#ef4444;}
</style>
</head>

<body>

<div class="container">
<h2>🛡️ AI Cyber Threat Email Analyzer</h2>

<form method="post" action="/predict">
<textarea name="email" required></textarea>
<br>
<button>Analyze</button>
</form>

<p>Model Accuracy: {{accuracy}}%</p>

{% if result %}

<h3 class="{{cls}}">{{result}}</h3>

<div class="section">
<b>AI Probability:</b><br>
Safe: {{safe}}%
<div class="bar"><div class="fill" style="width:{{safe}}%;background:green;"></div></div>

Spam: {{spam}}%
<div class="bar"><div class="fill" style="width:{{spam}}%;background:yellow;"></div></div>

Malicious: {{mal}}%
<div class="bar"><div class="fill" style="width:{{mal}}%;background:red;"></div></div>
</div>

<div class="section">
<b>Security Analysis:</b><br>
Suspicious Keywords: {{keywords}}<br>
Urgency Words: {{urgency}}<br>
Links Detected: {{links}}<br>
Email Length: {{length}} words<br>
</div>

<div class="section">
<b>Threat Score:</b> {{threat}} / 100
<div class="bar"><div class="fill" style="width:{{threat}}%;background:red;"></div></div>
</div>

<div class="section">
<b>AI Explanation:</b><br>
{{explanation}}
</div>

<div class="section">
<b>Security Advice:</b><br>
{{advice}}
</div>

{% endif %}
</div>

</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return render_template_string(html, accuracy=accuracy)

@app.route('/predict', methods=['POST'])
def predict():
    email_raw = request.form['email']
    email = clean_text(email_raw)

    data = vectorizer.transform([email])
    probs = model.predict_proba(data)[0]

    safe = round(probs[0]*100,2)
    spam = round(probs[1]*100,2)
    mal = round(probs[2]*100,2)

    pred = probs.argmax()

    if pred == 0:
        result = "✅ SAFE EMAIL"
        cls = "safe"
    elif pred == 1:
        result = "⚠️ SPAM DETECTED"
        cls = "spam"
    else:
        result = "🚨 MALICIOUS EMAIL"
        cls = "mal"

    # EXTRA ANALYSIS
    sec = analyze_security_features(email_raw)

    # EXPLANATION
    explanation = f"Detected {sec['keywords']} sensitive keywords, {sec['links']} links, and {sec['urgency']} urgency indicators."

    # ADVICE
    if mal > 50:
        advice = "Do NOT click links. This may be phishing."
    elif spam > 50:
        advice = "Likely spam. Avoid interacting."
    else:
        advice = "Looks safe, but stay cautious."

    return render_template_string(
        html,
        result=result,
        cls=cls,
        safe=safe,
        spam=spam,
        mal=mal,
        keywords=sec["keywords"],
        urgency=sec["urgency"],
        links=sec["links"],
        length=sec["length"],
        threat=sec["threat_score"],
        explanation=explanation,
        advice=advice,
        accuracy=accuracy
    )

if __name__ == "__main__":
    app.run(debug=True)