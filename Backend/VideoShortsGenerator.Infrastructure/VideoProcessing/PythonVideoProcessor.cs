using System.Diagnostics;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using VideoShortsGenerator.Application.Abstractions;

namespace VideoShortsGenerator.Infrastructure.VideoProcessing;

public sealed class PythonVideoProcessor : IVideoProcessor
{
    private readonly string _pythonExecutable;
    private readonly string _scriptPath;
    private readonly string _tempFolder;
    private readonly ILogger<PythonVideoProcessor> _logger;

    public PythonVideoProcessor(
        IConfiguration configuration,
        ILogger<PythonVideoProcessor> logger)
    {
        _logger = logger;

        _pythonExecutable = configuration["VideoProcessing:PythonPath"] ?? "python";

        _scriptPath = configuration["VideoProcessing:ScriptPath"]
            ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory,
                "VideoProcessing", "Scripts", "process_video.py");

        _tempFolder = configuration["VideoProcessing:TempFolder"]
            ?? Path.Combine(Path.GetTempPath(), "VideoProcessing");

        Directory.CreateDirectory(_tempFolder);
    }

    public async Task<Stream> ProcessAsync(
        string inputPath,
        CancellationToken cancellationToken = default)
    {
        if (!File.Exists(inputPath))
            throw new FileNotFoundException($"Input video not found: {inputPath}");

        if (!File.Exists(_scriptPath))
            throw new FileNotFoundException($"Python script not found: {_scriptPath}");

        var outputFileName = $"processed_{Guid.NewGuid()}.mp4";
        var outputPath = Path.Combine(_tempFolder, outputFileName);

        try
        {
            var processStartInfo = new ProcessStartInfo
            {
                FileName = _pythonExecutable,
                Arguments = $"\"{_scriptPath}\" \"{inputPath}\" \"{outputPath}\"",
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
        catch (Exception ex)
        {
            if (File.Exists(outputPath))
            {
                try { File.Delete(outputPath); } catch { }
            }

            _logger.LogError(ex, "Error processing video: {InputPath}", inputPath);
            throw new Exception($"Error processing video: {ex.Message}", ex);
        }
    }
}