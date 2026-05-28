const express = require("express");
const app = express();
app.use(express.json());

function sendEmail(to, data) {
    console.log("📧 Отправка Email на " + to);
    return true;
}

function sendSMS(to, data) {
    console.log("📱 Отправка SMS на " + to);
    return true;
}

function sendTelegram(to, data) {
    console.log("📨 Отправка Telegram пользователю " + to);
    return true;
}

function processTask(task) {
    console.log("Обработка задачи " + task.id + ", канал: " + task.channel);
    
    switch(task.channel) {
        case "email":
            return sendEmail(task.to, task.data);
        case "sms":
            return sendSMS(task.to, task.data);
        case "telegram":
            return sendTelegram(task.to, task.data);
        default:
            console.log("Неизвестный канал: " + task.channel);
            return false;
    }
}

let pendingTasks = [];

app.post("/task", (req, res) => {
    const task = req.body;
    pendingTasks.push(task);
    res.json({ status: "задача получена" });
});

app.get("/process", (req, res) => {
    if (pendingTasks.length === 0) {
        return res.json({ status: "очередь пуста" });
    }
    
    const task = pendingTasks.shift();
    const result = processTask(task);
    res.json({ 
        task_id: task.id, 
        processed: true, 
        success: result 
    });
});

app.listen(5002, () => {
    console.log("Worker запущен на порту 5002");
});
