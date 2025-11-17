// Task array to store all tasks
let tasks = [];
let currentFilter = 'all';

// DOM Elements
const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const taskList = document.getElementById('taskList');
const filterBtns = document.querySelectorAll('.filter-btn');
const clearCompletedBtn = document.getElementById('clearCompleted');
const emptyState = document.getElementById('emptyState');
const totalTasksEl = document.getElementById('totalTasks');
const activeTasksEl = document.getElementById('activeTasks');
const completedTasksEl = document.getElementById('completedTasks');

// Load tasks from localStorage on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    renderTasks();
    updateStats();
});

// Add task event listeners
addBtn.addEventListener('click', addTask);
taskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTask();
    }
});

// Filter buttons event listeners
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderTasks();
    });
});

// Clear completed tasks
clearCompletedBtn.addEventListener('click', clearCompleted);

// Add a new task
function addTask() {
    const taskText = taskInput.value.trim();
    
    if (taskText === '') {
        taskInput.focus();
        taskInput.classList.add('error');
        setTimeout(() => taskInput.classList.remove('error'), 500);
        return;
    }

    const task = {
        id: Date.now(),
        text: taskText,
        completed: false,
        createdAt: new Date().toISOString()
    };

    tasks.push(task);
    saveTasks();
    renderTasks();
    updateStats();
    
    taskInput.value = '';
    taskInput.focus();
}

// Render tasks based on current filter
function renderTasks() {
    taskList.innerHTML = '';
    
    const filteredTasks = tasks.filter(task => {
        if (currentFilter === 'active') return !task.completed;
        if (currentFilter === 'completed') return task.completed;
        return true;
    });

    if (filteredTasks.length === 0) {
        emptyState.classList.remove('hidden');
        taskList.style.display = 'none';
    } else {
        emptyState.classList.add('hidden');
        taskList.style.display = 'block';
        
        filteredTasks.forEach(task => {
            const taskItem = createTaskElement(task);
            taskList.appendChild(taskItem);
        });
    }
}

// Create task element
function createTaskElement(task) {
    const li = document.createElement('li');
    li.className = `task-item ${task.completed ? 'completed' : ''}`;
    li.dataset.id = task.id;

    li.innerHTML = `
        <div class="task-checkbox ${task.completed ? 'checked' : ''}" onclick="toggleTask(${task.id})">
            ${task.completed ? '<i class="fas fa-check"></i>' : ''}
        </div>
        <span class="task-text">${escapeHtml(task.text)}</span>
        <div class="task-actions">
            <button class="btn-edit" onclick="editTask(${task.id})" title="Edit task">
                <i class="fas fa-edit"></i>
            </button>
            <button class="btn-delete" onclick="deleteTask(${task.id})" title="Delete task">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;

    return li;
}

// Toggle task completion
function toggleTask(id) {
    const task = tasks.find(t => t.id === id);
    if (task) {
        task.completed = !task.completed;
        saveTasks();
        renderTasks();
        updateStats();
    }
}

// Edit task
function editTask(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    const taskItem = document.querySelector(`[data-id="${id}"]`);
    const taskTextEl = taskItem.querySelector('.task-text');
    const taskActions = taskItem.querySelector('.task-actions');

    // Create input field
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'task-input';
    input.value = task.text;

    // Replace text with input
    taskTextEl.replaceWith(input);
    input.focus();
    input.select();

    // Change edit button to save button
    taskActions.innerHTML = `
        <button class="btn-save" onclick="saveTask(${id})" title="Save task">
            <i class="fas fa-save"></i>
        </button>
        <button class="btn-delete" onclick="cancelEdit(${id})" title="Cancel">
            <i class="fas fa-times"></i>
        </button>
    `;

    // Save on Enter key
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            saveTask(id);
        }
    });
}

// Save edited task
function saveTask(id) {
    const taskItem = document.querySelector(`[data-id="${id}"]`);
    const input = taskItem.querySelector('.task-input');
    const newText = input.value.trim();

    if (newText === '') {
        input.focus();
        return;
    }

    const task = tasks.find(t => t.id === id);
    if (task) {
        task.text = newText;
        saveTasks();
        renderTasks();
        updateStats();
    }
}

// Cancel edit
function cancelEdit(id) {
    renderTasks();
}

// Delete task
function deleteTask(id) {
    tasks = tasks.filter(t => t.id !== id);
    saveTasks();
    renderTasks();
    updateStats();
}

// Clear completed tasks
function clearCompleted() {
    const completedCount = tasks.filter(t => t.completed).length;
    
    if (completedCount === 0) {
        return;
    }

    if (confirm(`Are you sure you want to delete ${completedCount} completed task(s)?`)) {
        tasks = tasks.filter(t => !t.completed);
        saveTasks();
        renderTasks();
        updateStats();
    }
}

// Update statistics
function updateStats() {
    const total = tasks.length;
    const active = tasks.filter(t => !t.completed).length;
    const completed = tasks.filter(t => t.completed).length;

    totalTasksEl.textContent = total;
    activeTasksEl.textContent = active;
    completedTasksEl.textContent = completed;
}

// Save tasks to localStorage
function saveTasks() {
    localStorage.setItem('tasks', JSON.stringify(tasks));
}

// Load tasks from localStorage
function loadTasks() {
    const storedTasks = localStorage.getItem('tasks');
    if (storedTasks) {
        tasks = JSON.parse(storedTasks);
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add error animation class to CSS
const style = document.createElement('style');
style.textContent = `
    .error {
        animation: shake 0.5s;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
`;
document.head.appendChild(style);
