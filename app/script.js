  <script>
const API_BASE = '/api';

let authToken = localStorage.getItem('auth_token') || null;

// Store all tasks
let tasks = [];
let currentPlanId = null;
let currentUser = null;


function toggleAuth(isReg) {
    document.getElementById('login-box').style.display = isReg ? 'none' : 'block';
    document.getElementById('reg-box').style.display = isReg ? 'block' : 'none';
}

// login
async function login(username, password, remember = false) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, password, remember })
        });

        const data = await response.json();
        if (data.success) {
            currentUser = data.user;
            return true;
        }
        return false;
    } catch (error) {
        console.error('Login error:', error);
        return false;
    }
}

// register
async function register(username, email, password) {
    try {
        console.log('register request:', { username, email });

        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username, email, password })
        });

        console.log('response status:', response.status);
        const data = await response.json();
        console.log('response data:', data);

        return data.success;
    } catch (error) {
        console.error('Register error:', error);
        return false;
    }
}

// logout
async function logout() {
    try {
        await fetch('/logout', {
            method: 'GET',
            credentials: 'include'
        });
        localStorage.removeItem('auth_token');
        location.reload();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

async function checkAuth() {
    try {
        const response = await fetch('/api/user', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const data = await response.json();
            currentUser = data;

            document.getElementById('hello-text').innerText = "Hello, " + currentUser.username;

            if (currentUser.role === 'admin') {
                document.body.classList.add('admin-mode');
                const adminPanel = document.getElementById('admin-panel');
                if (adminPanel) adminPanel.style.display = 'block';
            }

            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('app').style.display = 'grid';

            await loadTasks();
            await loadPosts();
            await loadHealthResources();
            return true;
        }
        return false;
    } catch (error) {
        return false;
    }
}

// Enter main app
async function enterApp() {
    const uInput = document.getElementById('username').value;
    const pInput = document.getElementById('password').value;

    if (!uInput || !pInput) {
        alert("Please enter username and password.");
        return;
    }

    const success = await login(uInput, pInput);

    if (success) {
        document.getElementById('hello-text').innerText = "Hello, " + currentUser.username;

        if (currentUser.role === 'admin') {
            document.body.classList.add('admin-mode');
            const adminPanel = document.getElementById('admin-panel');
            if (adminPanel) adminPanel.style.display = 'block';
        }

        document.getElementById('auth-screen').style.display = 'none';
        document.getElementById('app').style.display = 'grid';

        var now = new Date();
        var month = now.getMonth() + 1;
        var day = now.getDate();
        if (month < 10) month = "0" + month;
        if (day < 10) day = "0" + day;
        document.getElementById('todayVal').innerText = month + "/" + day;

        await loadTasks();
        await loadPosts();
        await loadHealthResources();
    } else {
        alert("Invalid username or password.");
    }
}

async function handleRegister() {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    if (!username || !email || !password) {
        alert("Please fill in all fields.");
        return;
    }

    console.log('Register');
    const success = await register(username, email, password);
    console.log('Register result:', success);

    if (success) {
        alert("Registration successful! Please login.");
        toggleAuth(false);
    } else {
        alert("Registration failed. Username or email may already exist.");
    }
}

// task
async function loadTasks() {
    try {
        const response = await fetch('/api/plans', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const plans = await response.json();

            if (plans.length > 0) {
                const plan = plans[0];
                currentPlanId = plan.id;
                tasks = plan.tasks.map(t => ({
                    id: t.id,
                    title: t.title,
                    type: t.type || t.type_emoji,
                    date: plan.deadline,
                    is_completed: t.is_completed,
                    estimated_hours: t.estimated_hours
                }));

                document.getElementById('deadlineVal').innerText = formatDateStr(plan.deadline);
                generateStudyPlan(tasks[0]?.id);
            }
        }
        renderTasks();
    } catch (error) {
        console.error('Error loading tasks:', error);
        renderTasks();
    }
}
sync function getTaskTypeId(typeName) {
    try {
        const response = await fetch('/api/task-types');
        if (response.ok) {
            const types = await response.json();
            const type = types.find(t => t.title === typeName);
            if (type) return type.id;
        }
    } catch (error) {
        console.error('Error fetching task types:', error);
    }
    const typeMap = {
        'Exam': 1,
        'Assignment': 2,
        'Quiz': 3
    };
    return typeMap[typeName] || 1;
}

// Render task list
function renderTasks() {
    var grid = document.getElementById('planGrid');
    var html = "";

    for (var i = 0; i < tasks.length; i++) {
        var t = tasks[i];
        var hours = t.estimated_hours || t.hours || 1;
        html += '<div class="task-card" onclick="generateStudyPlan(' + t.id + ')">';
        html += '<span class="type">' + t.type + '</span>';
        html += '<div class="card-actions">';
        html += '<button onclick="event.stopPropagation(); editTask(' + t.id + ')">&#9998;</button>';
        html += '<button onclick="event.stopPropagation(); deleteTask(' + t.id + ')">&#215;</button>';
        html += '</div>';
        html += '<h4>' + t.title + '</h4>';
        html += '<span class="due">Hours: ' + hours + 'h | Deadline: ' + t.date + '</span>';
        html += '</div>';
    }

    grid.innerHTML = html;


    if (tasks.length > 0) {
        generateStudyPlan(tasks[0].id);
    }
}

async function editTask(id) {
    var t = null;
    for (var i = 0; i < tasks.length; i++) {
        if (tasks[i].id === id) {
            t = tasks[i];
            break;
        }
    }

    var newTitle = prompt("Edit Task Name:", t.title);
    var newType = prompt("Edit Task Type (Exam/Assignment/Quiz):", t.type);

    if (newTitle) {
        try {
            const response = await fetch('/api/task/' + id, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    title: newTitle,
                    type_id: await getTaskTypeId(newType || t.type),
                    estimated_hours: t.estimated_hours || 1.0
                })
            });

            if (response.ok) {
                t.title = newTitle;
                if (newType) t.type = newType;
                renderTasks();
                generateStudyPlan(id);
            }
        } catch (error) {
            console.error('Error editing task:', error);
            t.title = newTitle;
            if (newType) t.type = newType;
            renderTasks();
            generateStudyPlan(id);
        }
    }
}

async function deleteTask(id) {
    if (confirm("Are you sure you want to delete this task?")) {
        try {
            const response = await fetch('/api/task/' + id, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (response.ok) {
                var newTasks = [];
                for (var i = 0; i < tasks.length; i++) {
                    if (tasks[i].id !== id) {
                        newTasks.push(tasks[i]);
                    }
                }
                tasks = newTasks;
                renderTasks();
                document.getElementById('phaseContent').classList.remove('active');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            var newTasks = [];
            for (var i = 0; i < tasks.length; i++) {
                if (tasks[i].id !== id) {
                    newTasks.push(tasks[i]);
                }
            }
            tasks = newTasks;
            renderTasks();
            document.getElementById('phaseContent').classList.remove('active');
        }
    }
}


function formatDateStr(dateStr) {
    if (!dateStr) return '--/--';
    const d = new Date(dateStr);
    const m = d.getMonth() + 1;
    const day = d.getDate();
    return (m < 10 ? "0" : "") + m + "/" + (day < 10 ? "0" : "") + day;
}

// community
async function loadPosts() {
    try {
        const response = await fetch('/api/posts', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const posts = await response.json();
            renderPosts(posts);
        }
    } catch (error) {
        console.error('Error loading posts:', error);
    }
}

function renderPosts(posts) {
    const postList = document.getElementById('postList');
    let html = '';

    for (const post of posts) {
        const isOwner = currentUser && (currentUser.id === post.author_id || currentUser.role === 'admin');
        html += '<div class="post-container">';
        html += '<span class="user-name">@' + post.author + ':</span>';
        if (isOwner) {
            html += '<div style="float:right;">';
            html += '<button onclick="editPost(' + post.id + ', \'' + escapeHtml(post.body) + '\')" style="background:none;border:none;cursor:pointer;margin-right:10px;">&#9998;</button>';
            html += '<button onclick="deletePost(' + post.id + ')" style="background:none;border:none;cursor:pointer;color:#cc7a7a;">&#215;</button>';
            html += '</div>';
        }
        html += '<span class="post-content">' + post.body + '</span>';
        html += '<div class="interact-zone">';
        html += '<span>Like (' + post.comment_count + ')</span>';
        html += '<span>Comment</span>';
        html += '</div>';
        html += '</div>';
    }

    postList.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

async function addPost() {
    var inputEl = document.getElementById('postInput');
    var val = inputEl.value;

    if (!val) return;

    try {
        const response = await fetch('/api/post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                title: 'Post',
                body: val
            })
        });

        if (response.ok) {
            var user = currentUser?.username || "Me";
            var newPostHtml = '<div class="post-container">';
            newPostHtml += '<span class="user-name">@' + user + ':</span>';
            newPostHtml += '<span class="post-content">' + val + '</span>';
            newPostHtml += '<div class="interact-zone">';
            newPostHtml += '<span>Like</span> · <span>Comment</span>';
            newPostHtml += '</div>';
            newPostHtml += '</div>';

            document.getElementById('postList').insertAdjacentHTML('afterbegin', newPostHtml);
        }
    } catch (error) {
        console.error('Error posting:', error);
        var user = currentUser?.username || "Me";
        var newPostHtml = '<div class="post-container">';
        newPostHtml += '<span class="user-name">@' + user + ':</span>';
        newPostHtml += '<span class="post-content">' + val + '</span>';
        newPostHtml += '<div class="interact-zone">';
        newPostHtml += '<span>Like</span> · <span>Comment</span>';
        newPostHtml += '</div>';
        newPostHtml += '</div>';

        document.getElementById('postList').insertAdjacentHTML('afterbegin', newPostHtml);
    }

    inputEl.value = "";
    inputEl.blur();
}

async function editPost(postId, currentBody) {
    const newBody = prompt("Edit your post:", currentBody);
    if (!newBody || newBody === currentBody) return;

    try {
        const formData = new FormData();
        formData.append('title', 'Post');
        formData.append('body', newBody);

        const response = await fetch('/post/' + postId + '/edit', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });

        if (response.ok || response.redirected) {
            loadPosts();
        } else {
            alert("Failed to edit post.");
        }
    } catch (error) {
        console.error('Error editing post:', error);
    }
}

async function deletePost(postId) {
    if (!confirm("Are you sure you want to delete this post?")) return;

    try {
        const response = await fetch('/post/' + postId + '/delete', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok || response.redirected) {
            loadPosts();
        } else {
            alert("Failed to delete post.");
        }
    } catch (error) {
        console.error('Error deleting post:', error);
    }
}

// health
async function loadHealthResources() {
    try {
        const response = await fetch('/api/health', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.ok) {
            const resources = await response.json();
            renderHealthPosts(resources);
        }
    } catch (error) {
        console.error('Error loading health resources:', error);
    }
}

function renderHealthPosts(resources) {
    const healthList = document.getElementById('healthPostList');
    if (!healthList) return;

    let html = '';
    for (const r of resources) {
        const isOwner = currentUser && (currentUser.role === 'admin' || currentUser.id === r.author_id);

        html += '<div class="post-container">';
        html += '<span class="category-tag" style="...">' + (r.category || 'Health') + '</span>';

        if (isOwner) {
            html += '<div style="float:right;">';
            html += '<button onclick="editHealthResource(' + r.id + ', \'' + escapeHtml(r.title || '') + '\', \'' + escapeHtml(r.content || '') + '\')" style="...">&#9998;</button>';
            html += '<button onclick="deleteHealthResource(' + r.id + ')" style="...">&#215;</button>';
            html += '</div>';
        }

        html += '<span class="user-name">@Health:</span>';
        html += '<span class="post-content"><strong>' + (r.title || '') + '</strong><br>' + r.content + '</span>';
        html += '<div class="interact-zone"><span>Like</span> · <span>Comment</span></div>';
        html += '</div>';
    }
    healthList.innerHTML = html;
}

    function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

async function addHealthPost() {
    var inputEl = document.getElementById('healthInput');
    var val = inputEl.value;

    if (!val) return;

    var user = currentUser?.username || "Me";
    var newPostHtml = '<div class="post-container">';
    newPostHtml += '<span class="category-tag" style="display:inline-block;background:#e9edc6;color:#6b705c;padding:3px 10px;border-radius:10px;font-size:12px;margin-bottom:10px;">Health Tip</span>';
    newPostHtml += '<span class="user-name">@' + user + ':</span>';
    newPostHtml += '<span class="post-content">' + val + '</span>';
    newPostHtml += '<div class="interact-zone">';
    newPostHtml += '<span>Like</span>';
    newPostHtml += '<span>Comment</span>';
    newPostHtml += '</div>';
    newPostHtml += '</div>';

    document.getElementById('healthPostList').insertAdjacentHTML('afterbegin', newPostHtml);

    inputEl.value = "";
    inputEl.blur();
}

async function editHealthResource(id, currentTitle, currentContent) {
    const newTitle = prompt("Edit title:", currentTitle);
    if (!newTitle || newTitle === currentTitle) return;

    try {
        const formData = new FormData();
        formData.append('title', newTitle);
        formData.append('category', 'other');
        formData.append('content', newContent);

        const response = await fetch('/health/' + id + '/edit', {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });

        if (response.ok || response.redirected) {
            loadHealthResources();
        } else {
            alert("Failed to edit.");
        }
    } catch (error) {
        console.error('Error editing health resource:', error);
    }
}

async function deleteHealthResource(id) {
    if (!confirm("Are you sure you want to delete this resource?")) return;

    try {
        const response = await fetch('/health/' + id + '/delete', {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok || response.redirected) {
            loadHealthResources();
        } else {
            alert("Failed to delete.");
        }
    } catch (error) {
        console.error('Error deleting health resource:', error);
    }
}


// Switch navigation tabs
function switchTab(id, el) {

    var navItems = document.querySelectorAll('.nav-item');
    for (var i = 0; i < navItems.length; i++) {
        navItems[i].classList.remove('active');
    }

    if (el) el.classList.add('active');


    var views = document.querySelectorAll('.view');
    for (var j = 0; j < views.length; j++) {
        views[j].classList.remove('active');
    }

    document.getElementById(id).classList.add('active');
}

async function addTask() {
    var title = document.getElementById('taskTitle').value;
    var date = document.getElementById('taskDate').value;
    var type = document.getElementById('taskType').value;
    var hours = document.getElementById('taskHours').value || 1;

    if (!title || !date) {
        alert("Please provide full mission details.");
        return;
    }

    if (!currentPlanId) {
        await createDefaultPlan(date);
    }

    try {
        const response = await fetch('/api/task', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                plan_id: currentPlanId,
                title: title,
                type_id: await getTaskTypeId(type),
                hours: parseFloat(hours)
            })
        });

        if (response.ok) {
            const data = await response.json();
            const newTask = {
                id: data.task.id,
                title: title,
                type: type,
                date: date,
                hours: parseFloat(hours)
            };
            tasks.push(newTask);
            renderTasks();
            document.getElementById('taskTitle').value = '';
        } else {
            alert("Failed to add task.");
        }
    } catch (error) {
        console.error('Error adding task:', error);
        const newTask = {
            id: Date.now(),
            title: title,
            type: type,
            date: date,
            hours: parseFloat(hours)
        };
        tasks.push(newTask);
        renderTasks();
        document.getElementById('taskTitle').value = '';
    }
}

// plan
async function createDefaultPlan(deadline) {
    try {
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                title: 'My Study Plan',
                deadline: deadline,
                tasks: []
            })
        });

        if (response.ok) {
            const data = await response.json();
            currentPlanId = data.plan.id;
        }
    } catch (error) {
        console.error('Error creating plan:', error);
    }
}


async function getTaskTypeId(typeName) {
    try {
        const response = await fetch('/api/task-types');
        if (response.ok) {
            const types = await response.json();
            const type = types.find(t => t.title === typeName);
            if (type) return type.id;
        }
    } catch (error) {
        console.error('Error fetching task types:', error);
    }
    const typeMap = {
        'Exam': 1,
        'Assignment': 2,
        'Quiz': 3
    };
    return typeMap[typeName] || 1;
}

// Render task list
function renderTasks() {
    var grid = document.getElementById('planGrid');
    var html = "";

    for (var i = 0; i < tasks.length; i++) {
        var t = tasks[i];
        var hours = t.estimated_hours || t.hours || 1;
        html += '<div class="task-card" onclick="generateStudyPlan(' + t.id + ')">';
        html += '<span class="type">' + t.type + '</span>';
        html += '<div class="card-actions">';
        html += '<button onclick="event.stopPropagation(); editTask(' + t.id + ')">&#9998;</button>';
        html += '<button onclick="event.stopPropagation(); deleteTask(' + t.id + ')">&#215;</button>';
        html += '</div>';
        html += '<h4>' + t.title + '</h4>';
        html += '<span class="due">Hours: ' + hours + 'h | Deadline: ' + t.date + '</span>';
        html += '</div>';
    }

    grid.innerHTML = html;


    if (tasks.length > 0) {
        generateStudyPlan(tasks[0].id);
    }
}

async function deleteTask(id) {
    if (confirm("Are you sure you want to delete this task?")) {
        try {
            const response = await fetch('/api/task/' + id, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (response.ok) {
                var newTasks = [];
                for (var i = 0; i < tasks.length; i++) {
                    if (tasks[i].id !== id) {
                        newTasks.push(tasks[i]);
                    }
                }
                tasks = newTasks;
                renderTasks();
                document.getElementById('phaseContent').classList.remove('active');
            }
        } catch (error) {
            console.error('Error deleting task:', error);
            var newTasks = [];
            for (var i = 0; i < tasks.length; i++) {
                if (tasks[i].id !== id) {
                    newTasks.push(tasks[i]);
                }
            }
            tasks = newTasks;
            renderTasks();
            document.getElementById('phaseContent').classList.remove('active');
        }
    }
}

async function editTask(id) {
    var t = null;
    for (var i = 0; i < tasks.length; i++) {
        if (tasks[i].id === id) {
            t = tasks[i];
            break;
        }
    }

    var newTitle = prompt("Edit Task Name:", t.title);
    var newType = prompt("Edit Task Type (Exam/Assignment/Quiz):", t.type);

    if (newTitle) {
        try {
            const response = await fetch('/api/task/' + id, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    title: newTitle,
                    type_id: await getTaskTypeId(newType || t.type),
                    estimated_hours: t.estimated_hours || 1.0
                })
            });

            if (response.ok) {
                t.title = newTitle;
                if (newType) t.type = newType;
                renderTasks();
                generateStudyPlan(id);
            }
        } catch (error) {
            console.error('Error editing task:', error);
            t.title = newTitle;
            if (newType) t.type = newType;
            renderTasks();
            generateStudyPlan(id);
        }
    }
}

// Generate study plan
function generateStudyPlan(taskId) {
    var task = null;
    for (var i = 0; i < tasks.length; i++) {
        if (tasks[i].id === taskId) {
            task = tasks[i];
            break;
        }
    }

    if (!task) return;

    var deadline = new Date(task.date);
    var now = new Date();


    var daysToDeadline = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));

    if (daysToDeadline <= 0) {
        alert("This mission has expired!");
        return;
    }


    function formatDate(d) {
        var m = d.getMonth() + 1;
        var day = d.getDate();
        if (m < 10) m = "0" + m;
        if (day < 10) day = "0" + day;
        return m + "/" + day;
    }


    var phase1End = new Date(now);
    phase1End.setDate(now.getDate() + Math.floor(daysToDeadline * 0.3));


    var phase2Start = new Date(phase1End);
    phase2Start.setDate(phase1End.getDate() + 1);
    var phase2End = new Date(phase1End);
    phase2End.setDate(phase1End.getDate() + Math.floor(daysToDeadline * 0.4));


    var phase3Start = new Date(phase2End);
    phase3Start.setDate(phase2End.getDate() + 1);


    document.getElementById('phase1-dates').innerText = formatDate(now) + " — " + formatDate(phase1End);
    document.getElementById('phase2-dates').innerText = formatDate(phase2Start) + " — " + formatDate(phase2End);
    document.getElementById('phase3-dates').innerText = formatDate(phase3Start) + " — " + formatDate(deadline);

    document.getElementById('deadlineVal').innerText = formatDate(deadline);
    document.getElementById('activeTaskTitle').innerText = task.title;

    document.getElementById('phaseContent').classList.add('active');
}

async function addPost() {
    var inputEl = document.getElementById('postInput');
    var val = inputEl.value;

    if (!val) return;

    try {
        const response = await fetch('/api/post', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                title: 'Post',
                body: val
            })
        });

        if (response.ok) {
            var user = currentUser?.username || "Me";
            var newPostHtml = '<div class="post-container">';
            newPostHtml += '<span class="user-name">@' + user + ':</span>';
            newPostHtml += '<span class="post-content">' + val + '</span>';
            newPostHtml += '<div class="interact-zone">';
            newPostHtml += '<span>Like</span> · <span>Comment</span>';
            newPostHtml += '</div>';
            newPostHtml += '</div>';

            document.getElementById('postList').insertAdjacentHTML('afterbegin', newPostHtml);
        }
    } catch (error) {
        console.error('Error posting:', error);
        var user = currentUser?.username || "Me";
        var newPostHtml = '<div class="post-container">';
        newPostHtml += '<span class="user-name">@' + user + ':</span>';
        newPostHtml += '<span class="post-content">' + val + '</span>';
        newPostHtml += '<div class="interact-zone">';
        newPostHtml += '<span>Like</span> · <span>Comment</span>';
        newPostHtml += '</div>';
        newPostHtml += '</div>';

        document.getElementById('postList').insertAdjacentHTML('afterbegin', newPostHtml);
    }

    inputEl.value = "";
    inputEl.blur();
}

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
});
    </script>
