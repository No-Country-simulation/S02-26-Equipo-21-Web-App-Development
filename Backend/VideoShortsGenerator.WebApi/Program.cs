using System;
using Microsoft.AspNetCore.Http.Features;
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

// Leer orígenes permitidos desde appsettings.json (se espera un array en "Cors:AllowedOrigins")
var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? Array.Empty<string>();

// Database
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");

builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseMySQL(connectionString));

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

//Additional settings to be able to upload files
builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.MaxRequestBodySize = 150 * 1024 * 1024; // 150 MB
});
builder.Services.Configure<FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 150 * 1024 * 1024; // 150 MB
});

// CORS - usar los orígenes leídos desde appsettings.json
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend",
        policy =>
        {
            policy.WithOrigins(allowedOrigins)
                  .AllowAnyHeader()
                  .AllowAnyMethod();
        });
});

var app = builder.Build();

// Configure HTTP pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

// Usar CORS
app.UseCors("AllowFrontend");

app.UseAuthorization();
app.MapControllers();

app.Run();