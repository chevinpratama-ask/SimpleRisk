from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    success = None
    error = None

    if request.method == 'POST':
        user_code = request.form.get('user_code')
        use_name = request.form.get('use_name')
        role = request.form.get('role')
        is_active = 'is_active' in request.form

        try:
            # Simulasi insert ke database atau logika lainnya
            print("User ditambahkan:", user_code, use_name, role, is_active)
            success = True
        except Exception as e:
            error = str(e)

    return render_template('add_user.html', success=success, error=error)

if __name__ == '__main__':
    app.run(debug=True)
