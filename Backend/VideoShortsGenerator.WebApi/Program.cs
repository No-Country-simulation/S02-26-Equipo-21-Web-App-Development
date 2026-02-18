using Microsoft.EntityFrameworkCore;
using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Application.EventHandlers;
using VideoShortsGenerator.Application.EventHandling;
using VideoShortsGenerator.Application.Services;
using VideoShortsGenerator.Domain.Repositories;
using VideoShortsGenerator.Infrastructure.BackgroundServices;
using VideoShortsGenerator.Infrastructure.Persistence;
using VideoShortsGenerator.Infrastructure.Storage;
using VideoShortsGenerator.Infrastructure.VideoProcessing;

var builder = WebApplication.CreateBuilder(args);

// Database
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseMySql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        ServerVersion.AutoDetect(builder.Configuration.GetConnectionString("DefaultConnection"))));

// Infrastructure
builder.Services.AddScoped<IVideoRepository, VideoRepository>();
builder.Services.AddScoped<IVideoProcessor, PythonVideoProcessor>();
builder.Services.AddScoped<IVideoStorage, LocalVideoStorage>();

// Domain Events
builder.Services.AddScoped<IEventDispatcher, DomainEventDispatcher>();

// Application Services
builder.Services.AddScoped<VideoJobEventHandler>();
builder.Services.AddScoped<VideoJobService>();
builder.Services.AddScoped<VideoJobQueryService>();

// Background Services
builder.Services.AddHostedService<VideoProcessingWorker>();

// API
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Configure HTTP pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();