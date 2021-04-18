from flask import Flask,render_template,request,flash,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_user,logout_user,current_user,UserMixin,login_required
from werkzeug.security import generate_password_hash,check_password_hash
import os

db_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),'app.db')

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='fb3dd457d242e665ca29b9835dabde6e727f45c5a9134ddae96350005adde1a2'


db=SQLAlchemy(app)
login_manager=LoginManager(app)

#employee model class

class User(db.Model,UserMixin):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(25),unique=True,nullable=False)
    email=db.Column(db.String(40),unique=True,nullable=False)
    password=db.Column(db.Text(),nullable=False)


    def __str__(self):
        return f"<User {self.username}>"



@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Employee(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(255),nullable=False)
    email=db.Column(db.String(255),nullable=False)
    phone_number=db.Column(db.Text())

    def __repr__(self):
        return f'<Employee {self.id}>'

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        return cls.query.order_by(Employee.id.desc()).all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


@app.route('/')
def index():
    employees=Employee.get_all()
    context={
        'title':"List of Employees",
        'employees':employees
    }
    return render_template('index.html',**context)

@login_required
@app.route('/add',methods=['GET','POST'])
def add_employee():
    if request.method == 'POST':
        name=request.form.get('name')
        email=request.form.get('email')
        phone_number=request.form.get('phone_number')

        print(name)
        print(email)
        print(phone_number)

        new_employee=Employee(name=name,email=email,phone_number=phone_number)

        new_employee.save()


        flash('Employee has been added successfully!')

        return redirect('/')

    # else:
    # flash("Failed to add employee to db")
    # return redirect(request.url)
        




    context={
        'title':"List of Employees"
    }
    
    return render_template('add.html',**context)

@login_required
@app.route('/delete/<int:id>')
def delete_employee(id):
    employee_to_delete=Employee.query.get(id)
    employee_to_delete.delete()

    flash("Student deleted successfully")

    return redirect('/')

@login_required
@app.route('/update/<int:id>',methods=['GET','POST'])
def update_employee_info(id):
    employee_to_update=Employee.query.get(id)

    if request.method == 'POST':
        employee_to_update.name=request.form.get('name')
        employee_to_update.email=request.form.get('email')
        employee_to_update.phone_number=request.form.get('phone_number')

        db.session.commit()

        flash("Employee Info Updated")

        return redirect('/')
        
    context={
        'employee':employee_to_update
    }
    return render_template('update.html',**context)


@app.route('/login',methods=["GET","POST"])
def login():
    
    email=request.form.get('email')
    password=request.form.get('password')

    user=User.query.filter_by(email=email).first()


    if user and check_password_hash(user.password,password):
        login_user(user)

        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/signup',methods=['GET','POST'])
def register():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        confirm=request.form.get('confirm')

        user=User.query.filter_by(email=email).first()

        if user is not None:
            flash(f"The user with email {email} already exists")

            return redirect(url_for('register'))

        username_exists=User.query.filter_by(username=username).first()

        if user is not None:
            flash(f"The username {username} is already taken")

            return redirect(url_for('register'))

        if password != password:
            
            flash(f"The passwords provided do not match")

            return redirect(url_for('register'))
        
        password_hash=generate_password_hash(password)

        new_user=User(username=username,email=email,password=password_hash)

        db.session.add(new_user)
        db.session.commit()
        flash("User created created successfully")
        return redirect(url_for('login'))


    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.shell_context_processor
def make_shell_context():
    return {
        'app':app,
        'db':db,
        'Employee':Employee,
        'User':User
    }

if __name__ == '__main__':
    app.run(debug=True)