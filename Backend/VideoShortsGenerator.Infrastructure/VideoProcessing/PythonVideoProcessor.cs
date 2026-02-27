using System.Diagnostics;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using VideoShortsGenerator.Application.Abstractions;
using VideoShortsGenerator.Domain.Enums;

namespace VideoShortsGenerator.Infrastructure.VideoProcessing;

public sealed class PythonVideoProcessor : IVideoProcessor
{
    private readonly string _pythonSimple;
    private readonly string _pythonAdvanced;
    private readonly string _scriptSimple;
    private readonly string _scriptAdvanced;
    private readonly string _tempFolder;
    private readonly ILogger<PythonVideoProcessor> _logger;

    public PythonVideoProcessor(IConfiguration configuration, ILogger<PythonVideoProcessor> logger)
    {
        _logger = logger;

        _pythonSimple = configuration["VideoProcessing:PythonPathSimple"] ?? "python";
        _pythonAdvanced = configuration["VideoProcessing:PythonPathAdvanced"] ?? _pythonSimple;

        _scriptSimple = configuration["VideoProcessing:ScriptPathSimple"]
            ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "VideoProcessing", "Scripts", "process_simple.py");

        _scriptAdvanced = configuration["VideoProcessing:ScriptPathAdvanced"]
            ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "VideoProcessing", "Scripts", "process_advanced.py");

        _tempFolder = configuration["VideoProcessing:TempFolder"] ?? Path.Combine(Path.GetTempPath(), "VideoProcessing");
        Directory.CreateDirectory(_tempFolder);
    }

    public async Task<Stream> ProcessAsync(string inputPath, ProcessingType processingType, string? paramsJson = null, CancellationToken cancellationToken = default)
    {
        var pythonExe = processingType == ProcessingType.Advanced ? _pythonAdvanced : _pythonSimple;
        var script = processingType == ProcessingType.Advanced ? _scriptAdvanced : _scriptSimple;

        if (!File.Exists(inputPath))
            throw new FileNotFoundException($"Input video not found: {inputPath}");
        if (!File.Exists(script))
            throw new FileNotFoundException($"Python script not found: {script}");
        if (!File.Exists(pythonExe))
            _logger.LogWarning("Python executable not found at {PythonExe}, attempting to run with name", pythonExe);

        var outputFileName = $"processed_{Guid.NewGuid()}.mp4";
        var outputPath = Path.Combine(_tempFolder, outputFileName);

        var argsBuilder = new StringBuilder();
        argsBuilder.Append($"\"{script}\" \"{inputPath}\" \"{outputPath}\"");
        if (!string.IsNullOrEmpty(paramsJson))
            argsBuilder.Append($" \"{paramsJson.Replace("\"", "\\\"")}\"");

        var processStartInfo = new ProcessStartInfo
        {
            FileName = pythonExe,
            Arguments = argsBuilder.ToString(),
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        using var process = new Process { StartInfo = processStartInfo };

        var outputBuilder = new StringBuilder();
        var errorBuilder = new StringBuilder();

        process.OutputDataReceived += (sender, args) =>
        {
            if (args.Data != null)
                outputBuilder.AppendLine(args.Data);
        };

        process.ErrorDataReceived += (sender, args) =>
        {
            if (args.Data != null)
                errorBuilder.AppendLine(args.Data);
        };

        process.Start();
        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        var timeoutMinutes = 30;
        var completed = await Task.Run(() =>
            process.WaitForExit(timeoutMinutes * 60 * 1000),
            cancellationToken);

        if (!completed)
        {
            process.Kill();
            throw new TimeoutException(
                $"Python script exceeded timeout of {timeoutMinutes} minutes");
        }

        if (process.ExitCode != 0)
        {
            var error = errorBuilder.ToString();
            throw new Exception(
                $"Python script failed with exit code {process.ExitCode}. Error: {error}");
        }

        if (!File.Exists(outputPath))
            throw new FileNotFoundException($"Processed video not found at: {outputPath}");

        var fileStream = new FileStream(
            outputPath,
            FileMode.Open,
            FileAccess.Read,
            FileShare.None,
            bufferSize: 4096,
            useAsync: true);

        return fileStream;
    }
}