from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.orm as so
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime, timezone
from flask_login import UserMixin
from typing import Optional

class User(db.Model, UserMixin):
    __tablename__='user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(63), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(119), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    role: so.Mapped[str]=so.mapped_column(sa.String(255),default='normal',index=True)

    
    plan: Mapped[list['StudyPlan']] = relationship(back_populates="student", cascade="all, delete-orphan")
    posts: Mapped[list['Post']] = relationship(back_populates="author", cascade="all, delete-orphan")
    comments: Mapped[list['Comment']] = relationship(back_populates="author", cascade="all, delete-orphan")
    resources: Mapped[list['HealthResource']]=relationship(back_populates="admin", cascade="all, delete-orphan")
    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class StudyPlan(db.Model):
    __tablename__ ='study_plan'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(256),index=True)
    student_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id',ondelete="CASCADE"), nullable=False, index=True)
    deadline: so.Mapped[datetime] = so.mapped_column(sa.DATE, nullable=False)
    is_archived: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    tasks: so.Mapped[list['StudyTask']]= relationship(back_populates='plan',cascade="all , delete-orphan")
    student: Mapped['User']=relationship(back_populates='plan')




class StudyTask(db.Model):
    __tablename__ ='study_task'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)
    
    
    is_completed: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    estimated_hours: so.Mapped[float] = so.mapped_column(sa.Float, default=1.0)
    
    plan_id: Mapped[int] = mapped_column(sa.ForeignKey("study_plan.id", ondelete="CASCADE"), nullable=False, index=True)
    plan: Mapped['StudyPlan'] = relationship(back_populates="tasks")
    task_type: Mapped[Optional['TaskType']]=relationship(back_populates='task')
    type_id: Mapped[Optional[int]]=mapped_column(sa.ForeignKey("task_type.id"),nullable=True,index=True)


class TaskType(db.Model):
    __tablename__='task_type'
    id: Mapped[int]=mapped_column(primary_key=True)
    title: Mapped[str]=mapped_column(sa.String(64),index=True)
    color: Mapped[str]=mapped_column(sa.String(32))
    emoji: Mapped[str]=mapped_column(sa.String(16))


    
    task: Mapped[list['StudyTask']]=relationship(back_populates='task_type')




class HealthResource(db.Model):
    __tablename__='healthresource'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(256))
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    category: so.Mapped[str] = so.mapped_column(sa.String(64)) 
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc), index=True)
    admin: Mapped[User]=relationship(back_populates='resources')
    admin_id: Mapped[int]=so.mapped_column(sa.ForeignKey('user.id',ondelete="CASCADE"),nullable=False,index=True)



class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(256))
    body: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc), index=True)
    
    author_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    author: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list['Comment']] = relationship(back_populates="post", cascade="all, delete-orphan")

class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.Text)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc), index=True)
    
    post_id: Mapped[int] = mapped_column(sa.ForeignKey("post.id", ondelete="CASCADE"), nullable=False)
    post: Mapped[Post] = relationship(back_populates="comments")
    
    author_id: Mapped[int] = mapped_column(sa.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    author: Mapped[User] = relationship(back_populates="comments")

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))




