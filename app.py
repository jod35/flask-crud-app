from flask import Flask,render_template,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
import os

db_path=os.path.join(os.path.dirname(os.path.realpath(__file__)),'app.db')

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='fb3dd457d242e665ca29b9835dabde6e727f45c5a9134ddae96350005adde1a2'


db=SQLAlchemy(app)

#employee model class

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

@app.route('/delete/<int:id>')
def delete_employee(id):
    employee_to_delete=Employee.query.get(id)
    employee_to_delete.delete()

    flash("Student deleted successfully")

    return redirect('/')

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




@app.shell_context_processor
def make_shell_context():
    return {
        'app':app,
        'db':db,
        'Employee':Employee
    }

if __name__ == '__main__':
    app.run(debug=True)