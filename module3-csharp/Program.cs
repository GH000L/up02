using System.Collections.Concurrent;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

var statusStorage = new ConcurrentDictionary<string, NotificationStatus>();

app.MapGet("/status/{id}", async (HttpContext context) =>
{
    var id = context.Request.RouteValues["id"]?.ToString();
    if (string.IsNullOrEmpty(id) || !statusStorage.ContainsKey(id))
    {
        context.Response.StatusCode = 404;
        await context.Response.WriteAsJsonAsync(new { error = "Уведомление не найдено" });
        return;
    }
    
    var status = statusStorage[id];
    await context.Response.WriteAsJsonAsync(status);
});

app.MapPost("/log", async (HttpContext context) =>
{
    var log = await context.Request.ReadFromJsonAsync<NotificationLog>();
    if (log == null || string.IsNullOrEmpty(log.NotificationId))
    {
        context.Response.StatusCode = 400;
        await context.Response.WriteAsJsonAsync(new { error = "Нет ID" });
        return;
    }
    
    var status = new NotificationStatus
    {
        NotificationId = log.NotificationId,
        Channel = log.Channel,
        Status = log.Status,
        SentAt = DateTime.UtcNow,
        Error = log.Error
    };
    
    statusStorage[log.NotificationId] = status;
    await context.Response.WriteAsJsonAsync(new { status = "записано" });
});

app.MapGet("/logs", () => statusStorage.Values.ToList());

app.Run("http://localhost:5003");

public class NotificationLog
{
    public string NotificationId { get; set; }
    public string Channel { get; set; }
    public string Status { get; set; }
    public string Error { get; set; }
}

public class NotificationStatus
{
    public string NotificationId { get; set; }
    public string Channel { get; set; }
    public string Status { get; set; }
    public DateTime SentAt { get; set; }
    public string Error { get; set; }
}
