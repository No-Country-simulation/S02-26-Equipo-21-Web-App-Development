using Microsoft.EntityFrameworkCore;
using VideoShortsGenerator.Domain.Entities;
using VideoShortsGenerator.Domain.Enums;

namespace VideoShortsGenerator.Infrastructure.Persistence;

public sealed class ApplicationDbContext : DbContext
{
    public DbSet<VideoJob> VideoJobs { get; set; } = null!;

    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<VideoJob>(entity =>
        {
            entity.ToTable("VideoJobs");

            entity.HasKey(e => e.Id);

            entity.Property(e => e.Id)
                .HasColumnType("char(36)")
                .IsRequired();

            entity.Property(e => e.InputPath)
                .HasMaxLength(500)
                .IsRequired();

            entity.Property(e => e.OutputPath)
                .HasMaxLength(500);

            // <-- Cambiado a longtext para MySQL
            entity.Property(e => e.Params)
                .HasColumnType("longtext")
                .IsRequired(false);

            // Mapear ProcessingType como int y usar el enum como default
            entity.Property(e => e.ProcessingType)
                .HasConversion<int>()
                .IsRequired()
                .HasDefaultValue(ProcessingType.Simple);

            entity.Property(e => e.Status)
                .HasConversion<int>()
                .IsRequired();

            entity.Property(e => e.CreatedAt)
                .HasColumnType("datetime")
                .IsRequired();

            entity.Property(e => e.CompletedAt)
                .HasColumnType("datetime");

            entity.Ignore(e => e.DomainEvents);

            entity.HasIndex(e => new { e.Status, e.CreatedAt })
                .HasDatabaseName("idx_status_createdat");

            entity.HasIndex(e => e.CreatedAt)
                .HasDatabaseName("idx_createdat");
        });

        base.OnModelCreating(modelBuilder);
    }
}