from flask import render_template, redirect, url_for, flash,request,abort,jsonify
from sqlalchemy.exc import IntegrityError
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import login_user, current_user, login_required, logout_user
from urllib.parse import urlsplit
from app.admin_recorator import admin_required

import requests
import random


from app import app
from app import db
from app.models import User, StudyTask, HealthResource, Post, Comment,TaskType,StudyPlan  
from app.forms import LoginForm, RegistrationForm, TaskForm, PostForm, CommentForm,TaskTypeForm,CreateplanForm,HealthForm




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)




@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    plan_id = request.args.get('planid')

    if plan_id:
        stmt = (sa.select(StudyPlan).options(
            so.joinedload(StudyPlan.tasks).joinedload(StudyTask.task_type)
        ).where(StudyPlan.id == int(plan_id)).where(StudyPlan.student_id == current_user.id))
        plan = db.session.scalars(stmt).unique().first()
        if plan is None:
            abort(404)
    else:
        stmt = (
            sa.select(StudyPlan)
            .options(so.joinedload(StudyPlan.tasks).joinedload(StudyTask.task_type))
            .where(StudyPlan.student_id == current_user.id)
            .where(StudyPlan.is_archived == False)
            .order_by(StudyPlan.deadline.asc())
            .limit(1)
        )
        plan = db.session.scalars(stmt).first()

    task_types = db.session.scalars(sa.select(TaskType)).all()

    quote = "Never forgive to be extraordinary"
    author = 'Sifan'
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=3)
        if response.status_code == 200:
            data = response.json()
            quote = data[0]['q']
            author = data[0]['a']
    except Exception as e:
        pass

    return render_template('index.html', plan=plan, task_types=task_types, quote=quote, author=author)

@app.route('/plan/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    form = CreateplanForm()
    tasktypelist = db.session.scalars(sa.select(TaskType)).all()
    
    
    
    if form.validate_on_submit():
        
        new_plan = StudyPlan(
            title=form.title.data,
            deadline=form.deadline.data,
            student_id=current_user.id
        )
        
        
        
        task_titles = request.form.getlist('task_titles[]')
        task_hours = request.form.getlist('task_hours[]')
        task_types = request.form.getlist('task_types[]')
        
        
        for title, hours,type_id in zip(task_titles, task_hours,task_types):
            if title.strip():
                new_task = StudyTask(
                    title=title,
                    estimated_hours=float(hours),
                    type_id=int(type_id) if type_id else None
                    
                )
                new_plan.tasks.append(new_task)
        
        db.session.add(new_plan)        
        db.session.commit()
        flash('Your plan has been set up successfully~')
        return redirect(url_for('index'))
        
    return render_template('create_plan.html', form=form,task_types=tasktypelist)

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.session.get(StudyTask, task_id)
    if not task or task.plan.student_id != current_user.id:
        abort(403)
        
    plan = task.plan
    
   
    if plan is None:
        abort(404)


    if len(plan.tasks) <= 1:
        flash('You need to keep at least one task in a plan!')
        return redirect(url_for('index', planid=plan.id))

    db.session.delete(task)
    db.session.commit()


    if all(t.is_completed for t in plan.tasks):
        plan.is_archived = True
        db.session.commit()
        flash(f'🎉 {plan.title} has all been done! Let\'s move to the next one!!')
        return redirect(url_for('index'))
    else:
        flash('Ths task has been removed!🔫')
        return redirect(url_for('index', planid=plan.id))


@app.route('/plan/<int:plan_id>/delete', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = db.session.get(StudyPlan, plan_id)
    if plan and plan.student_id == current_user.id:
        db.session.delete(plan)
        db.session.commit()
        flash('This Plan has been deleted!🧲')
    return redirect(url_for('index'))

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = db.session.get(StudyTask, task_id)
    if not task or task.plan.student_id != current_user.id:
        abort(403)

    
    status = request.form.get('status')
    task.is_completed = (status == 'finished')
    db.session.commit()

    
    plan = task.plan
    archived = False
    if all(t.is_completed for t in plan.tasks):
        plan.is_archived = True
        db.session.commit()
        archived = True


    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        return jsonify({'success': True, 'archived': archived, 'planid': plan.id})


    if archived:
        flash(f'🎉 {plan.title} has all been done! Let\'s move to the next one!!')
        return redirect(url_for('index'))
    else:
        ref = request.referrer
        if ref:
            return redirect(ref)
        return redirect(url_for('index', planid=plan.id))
 
 
    











@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task=db.session.get(StudyTask,task_id)
    if not task or task.plan.student_id != current_user.id:
        abort(403)
    form=TaskForm(obj=task)
    form.task_type.choices=[(t.id,f"{t.emoji}{t.title}") for t in db.session.scalars(sa.select(TaskType)).all()]
    if form.validate_on_submit():
        task.title = form.title.data
        task.estimated_hours = form.estimated_hours.data
        task.task_type=db.session.get(TaskType, form.task_type.data)
        
        db.session.commit()

    
        return redirect(url_for("index"))
    


    return render_template("taskedit.html",form=form)

@app.route('/plan/<int:plan_id>/add_task_quick', methods=['POST'])
@login_required
def add_task_quick(plan_id):
    plan = db.session.get(StudyPlan, plan_id) 
    if not plan or plan.student_id != current_user.id:
        abort(403)

    title = request.form.get('title')
    task_type_id = request.form.get('task_type_id') 
    hours = request.form.get('hours')

    if title and task_type_id and hours:
        task_type = db.session.get(TaskType, int(task_type_id))
        
        new_task = StudyTask(
            title=title,
            estimated_hours=float(hours),
            task_type=task_type,
            plan=plan 
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Quick task added successfully!')
    else:
        flash('Failed to add task. Please fill in all fields.')

    return redirect(url_for('index'))














@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now on!')
        return redirect(url_for('forum'))
    
  
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('forum.html', form=form, posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')
        return redirect(url_for('post_detail', post_id=post.id))
        
    return render_template('post_detail.html', post=post, form=form)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
        
   
    if post.author != current_user and current_user.role != 'admin':
        abort(403)
        
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.', 'success')
    return redirect(url_for('forum'))

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)

    if post.author != current_user and current_user.role != 'admin':
        abort(403)
        

    form = PostForm(obj=post)
    
    if form.validate_on_submit():
        form.populate_obj(post)
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('edit_forum.html', form=form, title="Edit Post")

@app.route('/comment/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_comment(comment_id):
   
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        abort(404)
        

    if comment.author != current_user and current_user.role != 'admin':
        abort(403)
        
 
    form = CommentForm(obj=comment)
    
    if form.validate_on_submit():
        form.populate_obj(comment)
        db.session.commit()
        flash('Your comment has been updated!')
        
        return redirect(url_for('post_detail', post_id=comment.post.id))
        
 
    return render_template('edit_forum.html', form=form, title="Edit Comment")

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id)
    if comment is None:
        abort(404)

    if comment.author != current_user and current_user.role != 'admin':
        abort(403)

    post_id = comment.post.id 
    
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.')

    return redirect(url_for('post_detail', post_id=post_id))






















@app.route('/health')
@login_required
def health():
    resources = HealthResource.query.all()
    return render_template('health.html', resources=resources)


@app.route('/tasktype',methods=['GET', 'POST'])
@login_required
def tasktype():
    form=TaskTypeForm()

    if form.validate_on_submit():
        MACARON_COLORS = [
            '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', 
            '#E8B4B8', '#D4A5A5', '#9DC8C8', '#A3E1DC', '#FAD02E'
        ]
        CUTE_EMOJIS = ['📚', '💻', '⏳', '🧠', '📸', '🎯', '🚀', '💡', '📌', '🔥', '⏱', '🔧']
        alreadyexist= db.session.scalars(sa.select(TaskType)).all()
        al_emoji=[c.emoji for c in alreadyexist]
        al_color=[c.color for c in alreadyexist]

        availble_emoji=[c for c in CUTE_EMOJIS if c not in al_emoji]
        availble_color=[c for c in MACARON_COLORS if c not in al_color]
        if  availble_color:
            color=random.choice(availble_color)
        else:
            color=random.choice(MACARON_COLORS)

        if  availble_emoji:
            emoji=random.choice(availble_emoji)
        else:
            emoji=random.choice(CUTE_EMOJIS)
        
        task_type=TaskType(title=form.title.data,emoji=emoji,color=color)
        db.session.add(task_type)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('task_add.html',form=form)

@app.route('/plan/<string:status>/display')
@login_required
def display_plan(status):
    
    
    
    if status == 'arch':
        stmt = sa.select(StudyPlan).where(StudyPlan.student_id == current_user.id).where(StudyPlan.is_archived == True)
    elif status=='unarch':
        stmt = sa.select(StudyPlan).where(StudyPlan.student_id == current_user.id).where(StudyPlan.is_archived == False)
    else:
        stmt = sa.select(StudyPlan).where(StudyPlan.student_id == current_user.id)

        
        
        
    
    plans = db.session.scalars(stmt).all()
    
    return render_template('plandisplay.html', plans=plans)










@app.route('/health/create',methods=['GET', 'POST'])
@login_required
@admin_required
def create_health():
    form=HealthForm()
    if form.validate_on_submit():
        new_resource = HealthResource(
            title=form.title.data,
            category=form.category.data,
            content=form.content.data,
            admin_id=current_user.id)
        
        db.session.add(new_resource)
        db.session.commit()
        flash("Your health resources have been submitted")



        return redirect(url_for('health'))
    return render_template('create_health.html', form=form)

@app.route('/health/<int:healthid>/edit',methods=['GET', 'POST'])
@login_required
@admin_required
def edit_health(healthid):
    health=db.one_or_404(sa.select(HealthResource).where(HealthResource.id==healthid))
    form=HealthForm(obj=health)
    if form.validate_on_submit():
        
        health.title=form.title.data
        health.category=form.category.data
        health.content=form.content.data
        health.admin_id=current_user.id
        
        
        db.session.commit()
        flash("Your health resources have been Edited")



        return redirect(url_for('health'))
    return render_template('create_health.html', form=form)

@app.route('/health/<int:healthid>/delete',methods=['POST'])
@login_required
@admin_required
def delete_health(healthid):
    health=db.one_or_404(sa.select(HealthResource).where(HealthResource.id==healthid))
    db.session.delete(health)
    db.session.commit()
    



    return redirect(url_for('health'))
   
