import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Load data with keep_default_na=False so 'None' is treated as string 'None'
csv_path = os.path.join(os.path.dirname(__file__), 'benchmark-results.csv')
df = pd.read_csv(csv_path, keep_default_na=False)

# Styling configurations
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 15

# Color and marker mappings
colors = {
    'None': '#7f8c8d',      # Gray (Unsynchronized / Corrupted)
    'Atomic': '#27ae60',    # Green (Fast & Hardware-accelerated)
    'Lock': '#e67e22',      # Orange (OpenMP Lock / Moderate contention)
    'Critical': '#c0392b'   # Red (Critical section / High contention)
}

markers = {
    'None': 'x',
    'Atomic': 'o',
    'Lock': 's',
    'Critical': '^'
}

output_dir = os.path.dirname(__file__)

# -------------------------------------------------------------------------
# Graph 1: Execution Time vs Threads (Line Chart)
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 6), dpi=300)

for mech in ['Critical', 'Lock', 'Atomic', 'None']:
    sub_df = df[df['Mechanism'] == mech].sort_values('Threads')
    linestyle = '--' if mech == 'None' else '-'
    label = f"{mech} (Unsynchronized / Corrupted)" if mech == 'None' else f"{mech} (Correct)"
    ax.plot(
        sub_df['Threads'], sub_df['Time (s)'],
        marker=markers[mech], markersize=8, linewidth=2.5,
        color=colors[mech], linestyle=linestyle, label=label
    )

# Customized annotation offsets to completely avoid overlap
custom_offsets = {
    ('None', 1): (0, -18),
    ('None', 2): (0, -18),
    ('None', 4): (0, -18),
    ('None', 8): (0, -18),
    ('Atomic', 1): (0, -18),
    ('Atomic', 2): (0, 10),
    ('Atomic', 4): (0, 10),
    ('Atomic', 8): (0, 10),
    ('Lock', 1): (24, -2),
    ('Lock', 2): (0, -18),
    ('Lock', 4): (0, -18),
    ('Lock', 8): (0, -18),
    ('Critical', 1): (-24, 6),
    ('Critical', 2): (0, 10),
    ('Critical', 4): (0, 10),
    ('Critical', 8): (0, 10),
}

for _, row in df.iterrows():
    mech = row['Mechanism']
    t = row['Threads']
    val = row['Time (s)']
    offset = custom_offsets.get((mech, t), (0, 10))
    ax.annotate(
        f"{val:.4f}s",
        (t, val),
        textcoords="offset points",
        xytext=offset,
        ha='center',
        fontsize=8.5,
        fontweight='bold',
        color=colors[mech]
    )

ax.set_title('Execution Time vs. Number of Threads (10,000,000 Increments)', pad=15)
ax.set_xlabel('Number of Threads')
ax.set_ylabel('Execution Time (seconds)')
ax.set_xticks([1, 2, 4, 8])
ax.set_xlim(0.4, 8.6)
ax.set_ylim(-0.05, 0.82)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(title='Synchronization Mechanism', frameon=True, framealpha=0.9, loc='upper left')

# Highlight Atomic efficiency callout
ax.annotate(
    'Atomic: Minimal scaling overhead\n(~0.07s - 0.08s across all threads)',
    xy=(4, 0.0770), xytext=(4.3, 0.22),
    arrowprops=dict(arrowstyle="->", color='#27ae60', lw=1.5),
    fontsize=9, fontweight='bold', color='#1e8449',
    bbox=dict(boxstyle="round,pad=0.4", fc="#eafaf1", ec="#27ae60", lw=1)
)

plt.tight_layout()
line_chart_path = os.path.join(output_dir, 'execution_time_comparison.png')
plt.savefig(line_chart_path, dpi=300)
plt.close()
print(f"Saved: {line_chart_path}")

# -------------------------------------------------------------------------
# Graph 2: Grouped Bar Chart of Execution Times
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

thread_counts = [1, 2, 4, 8]
x = np.arange(len(thread_counts))
width = 0.18
mechanisms = ['None', 'Atomic', 'Lock', 'Critical']

for i, mech in enumerate(mechanisms):
    times = [df[(df['Mechanism'] == mech) & (df['Threads'] == t)]['Time (s)'].values[0] for t in thread_counts]
    pos = x + (i - 1.5) * width
    bars = ax.bar(pos, times, width, label=mech, color=colors[mech], edgecolor='black', linewidth=0.8, alpha=0.9)
    
    # Value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.3f}s",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center', va='bottom',
            fontsize=7.5,
            fontweight='bold',
            rotation=0
        )

ax.set_title('Synchronization Overhead Across Thread Counts', pad=15)
ax.set_xlabel('Number of Threads')
ax.set_ylabel('Execution Time (seconds)')
ax.set_xticks(x)
ax.set_xticklabels([f"{t} Thread{'s' if t > 1 else ''}" for t in thread_counts])
ax.set_ylim(0, 0.82)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.legend(title='Mechanism', frameon=True, framealpha=0.9, loc='upper left')

plt.tight_layout()
bar_chart_path = os.path.join(output_dir, 'synchronization_overhead_comparison.png')
plt.savefig(bar_chart_path, dpi=300)
plt.close()
print(f"Saved: {bar_chart_path}")

# -------------------------------------------------------------------------
# Graph 3: Race Condition Impact (Final Count & Update Loss)
# -------------------------------------------------------------------------
none_df = df[df['Mechanism'] == 'None'].sort_values('Threads')
expected = 10000000

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)

# Left: Final Count vs Expected
threads = none_df['Threads'].values
counts = none_df['Final Count'].values
counts_millions = counts / 1e6

bars = ax1.bar([str(t) for t in threads], counts_millions, color='#e74c3c', edgecolor='black', width=0.55, alpha=0.85)
ax1.axhline(10.0, color='#27ae60', linestyle='--', linewidth=2, label='Expected Count (10M)')

for bar, count in zip(bars, counts):
    height = bar.get_height()
    ax1.annotate(
        f"{count:,}\n({height:.2f}M)",
        xy=(bar.get_x() + bar.get_width() / 2, height / 2),
        ha='center', va='center',
        fontsize=9, fontweight='bold', color='white'
    )

ax1.set_title('Unsynchronized Final Counter Value', pad=12)
ax1.set_xlabel('Number of Threads')
ax1.set_ylabel('Final Count (Millions)')
ax1.set_ylim(0, 11.5)
ax1.grid(True, axis='y', linestyle='--', alpha=0.5)
ax1.legend(loc='upper right')

# Right: Percentage of Lost Updates
loss_pct = [(expected - c) / expected * 100 for c in counts]
bars2 = ax2.bar([str(t) for t in threads], loss_pct, color='#c0392b', edgecolor='black', width=0.55, alpha=0.85)

for bar, pct in zip(bars2, loss_pct):
    height = bar.get_height()
    ax2.annotate(
        f"{pct:.1f}% Lost",
        xy=(bar.get_x() + bar.get_width() / 2, max(height, 2)),
        xytext=(0, 4), textcoords="offset points",
        ha='center', va='bottom',
        fontsize=9.5, fontweight='bold', color='#c0392b'
    )

ax2.set_title('Percentage of Lost Increments (Data Race)', pad=12)
ax2.set_xlabel('Number of Threads')
ax2.set_ylabel('Lost Updates (%)')
ax2.set_ylim(0, 100)
ax2.grid(True, axis='y', linestyle='--', alpha=0.5)

plt.suptitle('Race Condition Severity in Unsynchronized Execution (10,000,000 Target)', fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
race_chart_path = os.path.join(output_dir, 'race_condition_loss.png')
plt.savefig(race_chart_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {race_chart_path}")

# -------------------------------------------------------------------------
# Graph 4: Comprehensive 2x2 Summary Dashboard
# -------------------------------------------------------------------------
fig, axs = plt.subplots(2, 2, figsize=(14, 11), dpi=300)

# (0, 0): Scaling Line Chart
ax = axs[0, 0]
for mech in ['Critical', 'Lock', 'Atomic', 'None']:
    sub_df = df[df['Mechanism'] == mech].sort_values('Threads')
    linestyle = '--' if mech == 'None' else '-'
    ax.plot(
        sub_df['Threads'], sub_df['Time (s)'],
        marker=markers[mech], markersize=7, linewidth=2.2,
        color=colors[mech], linestyle=linestyle, label=mech
    )
ax.set_title('Execution Time Scaling (10M Increments)')
ax.set_xlabel('Threads')
ax.set_ylabel('Time (s)')
ax.set_xticks([1, 2, 4, 8])
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left', frameon=True)

# (0, 1): Grouped Bar Chart
ax = axs[0, 1]
for i, mech in enumerate(mechanisms):
    times = [df[(df['Mechanism'] == mech) & (df['Threads'] == t)]['Time (s)'].values[0] for t in thread_counts]
    pos = x + (i - 1.5) * width
    ax.bar(pos, times, width, label=mech, color=colors[mech], edgecolor='black', linewidth=0.7)
ax.set_title('Execution Overhead Comparison')
ax.set_xlabel('Threads')
ax.set_ylabel('Time (s)')
ax.set_xticks(x)
ax.set_xticklabels([f"{t}T" for t in thread_counts])
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.legend(loc='upper left', frameon=True)

# (1, 0): Race Condition Severity
ax = axs[1, 0]
ax.plot(threads, counts_millions, marker='o', markersize=8, color='#c0392b', linewidth=2.5, label='Actual Count')
ax.axhline(10.0, color='#27ae60', linestyle='--', linewidth=2, label='Expected Count (10M)')
ax.annotate("10.00M", (threads[0], counts_millions[0]), textcoords="offset points", xytext=(-20, -15), ha='center', fontsize=9, fontweight='bold', color='#c0392b')
for t, cm in zip(threads[1:], counts_millions[1:]):
    ax.annotate(f"{cm:.2f}M", (t, cm), textcoords="offset points", xytext=(0, -15), ha='center', fontsize=9, fontweight='bold', color='#c0392b')
ax.set_title('Race Condition: Actual vs Expected Count (Unsynchronized)')
ax.set_xlabel('Threads')
ax.set_ylabel('Final Count (Millions)')
ax.set_xticks([1, 2, 4, 8])
ax.set_ylim(0, 11)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='lower left', frameon=True)

# (1, 1): Relative Slowdown factor compared to Atomic (at 1, 2, 4, 8 threads)
ax = axs[1, 1]
atomic_times = [df[(df['Mechanism'] == 'Atomic') & (df['Threads'] == t)]['Time (s)'].values[0] for t in thread_counts]

for mech in ['Lock', 'Critical']:
    mech_times = [df[(df['Mechanism'] == mech) & (df['Threads'] == t)]['Time (s)'].values[0] for t in thread_counts]
    slowdown = [m / a for m, a in zip(mech_times, atomic_times)]
    ax.plot(thread_counts, slowdown, marker=markers[mech], markersize=8, linewidth=2.5, color=colors[mech], label=f"{mech} vs. Atomic")
    for t, s in zip(thread_counts, slowdown):
        # Prevent 1T overlap
        if t == 1:
            y_off = 10 if mech == 'Critical' else -18
        else:
            y_off = 8
        ax.annotate(f"{s:.1f}x", (t, s), textcoords="offset points", xytext=(0, y_off), ha='center', fontsize=9, fontweight='bold', color=colors[mech])

ax.axhline(1.0, color='#27ae60', linestyle=':', linewidth=1.8, label='Atomic Baseline (1.0x)')
ax.set_title('Relative Slowdown Compared to Atomic Mechanism')
ax.set_xlabel('Threads')
ax.set_ylabel('Slowdown Multiplier')
ax.set_xticks([1, 2, 4, 8])
ax.set_ylim(0, 11.5)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper left', frameon=True)

plt.suptitle('Benchmark Analysis: Synchronization Mechanisms in OpenMP', fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
summary_chart_path = os.path.join(output_dir, 'benchmark_summary.png')
plt.savefig(summary_chart_path, dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved: {summary_chart_path}")
