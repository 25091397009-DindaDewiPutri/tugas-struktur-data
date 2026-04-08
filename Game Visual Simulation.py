import sys
import time
import os
from collections import deque

# ─────────────────────────────────────────────
#  MAZE  (# = dinding, S = start, E = exit)
# ─────────────────────────────────────────────
RAW_MAZE = [
    "####################",
    "#S  #     #        #",
    "# ## # ## # ##### ##",
    "# #  #  # #     #  #",
    "# # ## ## ##### # ##",
    "#   #  #     #  #  #",
    "### # ### ## # ### #",
    "#   #   # #  #   # #",
    "# ### # # # ### # ##",
    "# #   # # #   # #  #",
    "# # ### # ### # ## #",
    "#   #   #   # #    #",
    "# ### ####### # ## #",
    "#   #         #  # #",
    "### ########### # ##",
    "#   #       #   #  #",
    "# ### ##### # ###  #",
    "#     #     #   #  #",
    "####### ######### ##",
    "#                 E#",
    "####################",
]

ROWS = len(RAW_MAZE)
COLS = max(len(row) for row in RAW_MAZE)
DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# ─────────────────────────────────────────────
#  WARNA TERMINAL (ANSI)
# ─────────────────────────────────────────────
RESET      = "\033[0m"
BOLD       = "\033[1m"

BG_WALL    = "\033[48;5;235m"   # abu gelap
BG_OPEN    = "\033[48;5;255m"   # putih
BG_VISITED = "\033[48;5;117m"   # biru muda
BG_PATH    = "\033[48;5;85m"    # hijau muda
BG_CURRENT = "\033[48;5;33m"    # biru terang
BG_START   = "\033[48;5;35m"    # hijau
BG_END     = "\033[48;5;214m"   # oranye

FG_WHITE   = "\033[97m"
FG_DARK    = "\033[30m"
FG_YELLOW  = "\033[93m"
FG_GREEN   = "\033[92m"
FG_CYAN    = "\033[96m"


def supports_color():
    """Cek apakah terminal mendukung warna ANSI."""
    if os.name == "nt":
        try:
            import ctypes
            kernel = ctypes.windll.kernel32
            # aktifkan Virtual Terminal Processing
            kernel.SetConsoleMode(kernel.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def clear():
    """Bersihkan layar terminal."""
    if os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


# ─────────────────────────────────────────────
#  PARSE MAZE
# ─────────────────────────────────────────────
def parse_maze():
    """Baca RAW_MAZE dan kembalikan grid, posisi start, dan posisi end."""
    grid = []
    start = end = None
    for r, row in enumerate(RAW_MAZE):
        line = list(row.ljust(COLS, "#"))
        grid.append(line)
        for c, ch in enumerate(line):
            if ch == "S":
                start = (r, c)
            elif ch == "E":
                end = (r, c)
    if start is None or end is None:
        raise ValueError("Maze harus memiliki karakter 'S' (start) dan 'E' (exit).")
    return grid, start, end


# ─────────────────────────────────────────────
#  SOLVER : BFS (jalur terpendek)
# ─────────────────────────────────────────────
def bfs(grid, start, end):
    """
    Breadth-First Search — menjamin jalur terpendek.
    Mengembalikan list langkah: (visited, current, path)
    - visited  : set posisi yang sudah dikunjungi
    - current  : posisi yang sedang diproses (None di langkah terakhir)
    - path     : frozenset jalur solusi (hanya ada di langkah terakhir)
    """
    visited = {start}
    prev    = {start: None}
    queue   = deque([start])
    steps   = []
    found   = False

    while queue:
        cur = queue.popleft()
        steps.append((frozenset(visited), cur, None))

        if cur == end:
            found = True
            break

        r, c = cur
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            nk = (nr, nc)
            if (0 <= nr < ROWS and 0 <= nc < COLS
                    and nk not in visited
                    and grid[nr][nc] != "#"):
                visited.add(nk)
                prev[nk] = cur
                queue.append(nk)

    # rekonstruksi jalur
    path = _trace_path(prev, end) if found else frozenset()
    steps.append((frozenset(visited), None, path))
    return steps, found


# ─────────────────────────────────────────────
#  SOLVER : DFS
# ─────────────────────────────────────────────
def dfs(grid, start, end):
    """
    Depth-First Search — tidak menjamin jalur terpendek.
    Format langkah sama dengan BFS.
    """
    visited = set()
    prev    = {start: None}
    stack   = [start]
    steps   = []
    found   = False

    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        steps.append((frozenset(visited), cur, None))

        if cur == end:
            found = True
            break

        r, c = cur
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            nk = (nr, nc)
            if (0 <= nr < ROWS and 0 <= nc < COLS
                    and nk not in visited
                    and grid[nr][nc] != "#"):
                if nk not in prev:
                    prev[nk] = cur
                stack.append(nk)

    path = _trace_path(prev, end) if found else frozenset()
    steps.append((frozenset(visited), None, path))
    return steps, found


def _trace_path(prev, end):
    """Rekonstruksi jalur dari dict prev secara mundur dari end ke start."""
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev.get(node)
    return frozenset(path)


# ─────────────────────────────────────────────
#  RENDER MAZE KE TERMINAL
# ─────────────────────────────────────────────
def render(grid, visited, current, path, step_num, total,
           algo_name, done, use_color):
    """Gambar state maze saat ini ke stdout."""
    lines = []

    # ── header ──
    title = f"  MAZE SOLVER  —  {algo_name}"
    sep   = "=" * 48
    if use_color:
        lines.append(BOLD + FG_CYAN + sep + RESET)
        lines.append(BOLD + FG_CYAN + title + RESET)
        lines.append(BOLD + FG_CYAN + sep + RESET)
    else:
        lines.append(sep)
        lines.append(title)
        lines.append(sep)

    # ── grid ──
    for r in range(ROWS):
        row_str = ""
        for c in range(COLS):
            ch  = grid[r][c]
            pos = (r, c)

            if use_color:
                if ch == "S":
                    row_str += BG_START + FG_WHITE + BOLD + " S" + RESET
                elif ch == "E":
                    row_str += BG_END + FG_DARK + BOLD + " E" + RESET
                elif ch == "#":
                    row_str += BG_WALL + "  " + RESET
                elif path and pos in path:
                    row_str += BG_PATH + FG_DARK + " *" + RESET
                elif current and pos == current:
                    row_str += BG_CURRENT + FG_WHITE + " @" + RESET
                elif visited and pos in visited:
                    row_str += BG_VISITED + FG_DARK + " ." + RESET
                else:
                    row_str += BG_OPEN + "  " + RESET
            else:
                # fallback tanpa warna
                if ch == "S":
                    row_str += " S"
                elif ch == "E":
                    row_str += " E"
                elif ch == "#":
                    row_str += "##"
                elif path and pos in path:
                    row_str += " *"
                elif current and pos == current:
                    row_str += " @"
                elif visited and pos in visited:
                    row_str += " ."
                else:
                    row_str += "  "
        lines.append(row_str)

    # ── progress bar ──
    lines.append("")
    bar_total  = 38
    pct        = min(step_num / max(total, 1), 1.0)
    filled     = int(bar_total * pct)
    bar        = "█" * filled + "░" * (bar_total - filled)
    pct_int    = int(pct * 100)
    lines.append(f"  Langkah : {step_num:>5} / {total}  [{bar}] {pct_int:>3}%")

    # ── status bawah ──
    if done:
        path_len = len(path) if path else 0
        vis_len  = len(visited) if visited else 0
        if path_len:
            msg = (f"  ✓ Selesai!  Panjang jalur: {path_len} sel  |"
                   f"  Dikunjungi: {vis_len} sel")
        else:
            msg = "  ✗ Tidak ada jalur ditemukan!"
        if use_color:
            lines.append(BOLD + FG_GREEN + msg + RESET)
        else:
            lines.append(msg)
    else:
        lines.append("  Menjelajahi...  (Ctrl+C untuk berhenti)")

    # ── legenda ──
    lines.append("")
    if use_color:
        legend = (
            "  Legenda: "
            + BG_START   + " S " + RESET + " Start   "
            + BG_END     + " E " + RESET + " Exit   "
            + BG_CURRENT + " @ " + RESET + " Sedang  "
            + BG_VISITED + " . " + RESET + " Dikunjungi  "
            + BG_PATH    + " * " + RESET + " Jalur  "
            + BG_WALL    + "  "  + RESET + " Dinding"
        )
    else:
        legend = "  Legenda: S=Start  E=Exit  @=Sedang  .=Dikunjungi  *=Jalur  #=Dinding"
    lines.append(legend)
    lines.append("")

    # tulis sekaligus (lebih sedikit flickering)
    output = "\033[H" + "\n".join(lines) if use_color else "\n".join(lines)
    sys.stdout.write(output)
    sys.stdout.flush()


# ─────────────────────────────────────────────
#  MENU INTERAKTIF
# ─────────────────────────────────────────────
def menu():
    """Tampilkan menu dan kembalikan (algo_name, delay_detik)."""
    clear()
    print(BOLD + FG_CYAN + "=" * 48 + RESET)
    print(BOLD + FG_CYAN + "     MAZE SOLVER — PILIH ALGORITMA" + RESET)
    print(BOLD + FG_CYAN + "=" * 48 + RESET)
    print()
    print("  [1]  BFS  — Breadth-First Search  (jalur terpendek)")
    print("  [2]  DFS  — Depth-First Search")
    print()

    while True:
        try:
            choice = input("  Pilih algoritma (1/2): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Program dihentikan.")
            sys.exit(0)
        if choice in ("1", "2"):
            break
        print("  ⚠  Masukkan 1 atau 2.")

    print()
    print("  Kecepatan animasi:")
    print("  [1] Lambat (0.10 dtk)    [2] Normal (0.03 dtk)")
    print("  [3] Cepat  (0.008 dtk)   [4] Turbo  (tanpa animasi)")
    print()

    while True:
        try:
            spd = input("  Pilih kecepatan (1–4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Program dihentikan.")
            sys.exit(0)
        if spd in ("1", "2", "3", "4"):
            break
        print("  ⚠  Masukkan angka 1, 2, 3, atau 4.")

    algo  = "BFS" if choice == "1" else "DFS"
    delay = [0.10, 0.03, 0.008, 0][int(spd) - 1]
    return algo, delay


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    use_color = supports_color()

    # sembunyikan kursor selama animasi agar rapi
    if use_color:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    try:
        grid, start, end = parse_maze()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    while True:
        algo, delay = menu()

        # siapkan layar animasi
        clear()
        if use_color:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()

        # jalankan solver
        if algo == "BFS":
            steps, found = bfs(grid, start, end)
        else:
            steps, found = dfs(grid, start, end)

        total = len(steps)

        # ── animasi ──
        try:
            for i, (vis, cur, pth) in enumerate(steps):
                done = (pth is not None)
                render(grid, vis, cur, pth,
                       i + 1, total, algo, done, use_color)
                if delay > 0:
                    time.sleep(delay)
        except KeyboardInterrupt:
            print("\n\n  Animasi dihentikan oleh pengguna.")

        # ── ringkasan akhir ──
        print()
        last_vis, _, last_path = steps[-1]
        path_len = len(last_path) if last_path else 0
        vis_len  = len(last_vis)

        if use_color:
            print(BOLD + f"  Algoritma   : {algo}" + RESET)
            print(f"  Total langkah: {total}")
            print(f"  Sel dikunjungi: {vis_len}")
            if found:
                print(BOLD + FG_GREEN + f"  Panjang jalur: {path_len} sel" + RESET)
            else:
                print(BOLD + "\033[91m" + "  Tidak ada jalur!" + RESET)
        else:
            print(f"  Algoritma    : {algo}")
            print(f"  Total langkah: {total}")
            print(f"  Sel dikunjungi: {vis_len}")
            print(f"  Panjang jalur: {path_len if found else 'Tidak ditemukan'}")

        print()

        # ── tanya lagi ──
        try:
            again = input("  Jalankan lagi? (y/n): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            again = "n"

        if again != "y":
            print()
            print("  Terima kasih! Program selesai.")
            print()
            break


if __name__ == "__main__":
    # aktifkan warna ANSI di Windows sejak awal
    if os.name == "nt":
        os.system("color")
    main()
    # tampilkan kursor kembali saat program selesai
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()