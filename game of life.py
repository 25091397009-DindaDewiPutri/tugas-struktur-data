import random
import time
import os
import sys

# ============================================================
#  GAME OF LIFE - Conway's Game of Life dengan Menu Acak
# ============================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_empty_grid(rows, cols):
    return [[0] * cols for _ in range(rows)]

def create_random_grid(rows, cols, density=0.3):
    """Buat grid acak dengan kepadatan tertentu (0.0 - 1.0)"""
    grid = create_empty_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = 1 if random.random() < density else 0
    return grid

def create_pattern_grid(rows, cols, pattern_name):
    """Buat grid dengan pola tertentu di tengah"""
    grid = create_empty_grid(rows, cols)
    cx = rows // 2
    cy = cols // 2

    patterns = {
        "glider": [
            (0, 1), (1, 2),
            (2, 0), (2, 1), (2, 2)
        ],
        "blinker": [
            (0, 0), (0, 1), (0, 2)
        ],
        "block": [
            (0, 0), (0, 1),
            (1, 0), (1, 1)
        ],
        "r_pentomino": [
            (0, 1), (0, 2),
            (1, 0), (1, 1),
            (2, 1)
        ],
        "pulsar": [
            (-6,-4),(-6,-3),(-6,-2),(-6,2),(-6,3),(-6,4),
            (-4,-6),(-4,-1),(-4,1),(-4,6),
            (-3,-6),(-3,-1),(-3,1),(-3,6),
            (-2,-6),(-2,-1),(-2,1),(-2,6),
            (-1,-4),(-1,-3),(-1,-2),(-1,2),(-1,3),(-1,4),
            (1,-4),(1,-3),(1,-2),(1,2),(1,3),(1,4),
            (2,-6),(2,-1),(2,1),(2,6),
            (3,-6),(3,-1),(3,1),(3,6),
            (4,-6),(4,-1),(4,1),(4,6),
            (6,-4),(6,-3),(6,-2),(6,2),(6,3),(6,4),
        ],
        "spaceship": [
            (0,1),(0,4),
            (1,0),
            (2,0),(2,4),
            (3,0),(3,1),(3,2),(3,3),
        ],
        "acorn": [
            (0,1),
            (1,3),
            (2,0),(2,1),(2,4),(2,5),(2,6)
        ],
    }

    cells = patterns.get(pattern_name, patterns["glider"])
    for (dr, dc) in cells:
        r, c = cx + dr, cy + dc
        if 0 <= r < rows and 0 <= c < cols:
            grid[r][c] = 1
    return grid

def count_neighbors(grid, row, col, rows, cols):
    """Hitung jumlah tetangga hidup dari sebuah sel"""
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr = (row + dr) % rows  # Toroidal (grid melingkar)
            nc = (col + dc) % cols
            count += grid[nr][nc]
    return count

def next_generation(grid, rows, cols):
    """Hitung generasi berikutnya"""
    new_grid = create_empty_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            neighbors = count_neighbors(grid, r, c, rows, cols)
            if grid[r][c] == 1:
                # Aturan: Sel hidup
                new_grid[r][c] = 1 if neighbors in [2, 3] else 0
            else:
                # Aturan: Sel mati
                new_grid[r][c] = 1 if neighbors == 3 else 0
    return new_grid

def count_alive(grid):
    return sum(sum(row) for row in grid)

def render_grid(grid, rows, cols, gen, alive, mode_name):
    """Render grid ke terminal"""
    ALIVE = '█'
    DEAD  = '·'

    # Header
    print("=" * (cols + 2))
    print(f"  GAME OF LIFE  |  Mode: {mode_name}  |  Gen: {gen}  |  Hidup: {alive}")
    print("=" * (cols + 2))

    # Grid
    for r in range(rows):
        row_str = '|'
        for c in range(cols):
            row_str += ALIVE if grid[r][c] == 1 else DEAD
        row_str += '|'
        print(row_str)

    print("=" * (cols + 2))
    print("  [q] Keluar   [r] Ulang   [m] Menu")

def run_simulation(grid, rows, cols, mode_name, max_gen=500, delay=0.1):
    """Jalankan simulasi"""
    gen = 0
    try:
        while gen < max_gen:
            alive = count_alive(grid)
            clear_screen()
            render_grid(grid, rows, cols, gen, alive, mode_name)

            # Cek input non-blocking (hanya di terminal yang mendukung)
            grid = next_generation(grid, rows, cols)
            gen += 1
            time.sleep(delay)

            if alive == 0:
                print("\n  Semua sel mati! Simulasi selesai.")
                time.sleep(2)
                break
    except KeyboardInterrupt:
        pass

def show_menu():
    """Tampilkan menu utama"""
    clear_screen()
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║        CONWAY'S GAME OF LIFE         ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    print("  Pilih Mode:")
    print()
    print("  [1] 🎲 Acak - Kepadatan Rendah  (20%)")
    print("  [2] 🎲 Acak - Kepadatan Sedang  (40%)")
    print("  [3] 🎲 Acak - Kepadatan Tinggi  (60%)")
    print("  [4] 🎲 Acak - Penuh             (80%)")
    print()
    print("  [5] ✨ Pola: Glider")
    print("  [6] ✨ Pola: Blinker")
    print("  [7] ✨ Pola: Block (Still Life)")
    print("  [8] ✨ Pola: R-Pentomino (Chaos!)")
    print("  [9] ✨ Pola: Pulsar (Oscillator)")
    print("  [A] ✨ Pola: Spaceship")
    print("  [B] ✨ Pola: Acorn (Long running)")
    print()
    print("  [C] ⚙️  Atur Ukuran Grid Custom")
    print("  [Q] ❌ Keluar")
    print()
    print("  ══════════════════════════════════════")

def get_grid_size():
    """Minta ukuran grid dari user"""
    print()
    try:
        rows = int(input("  Masukkan jumlah baris (10-40): ").strip())
        cols = int(input("  Masukkan jumlah kolom (20-80): ").strip())
        rows = max(10, min(40, rows))
        cols = max(20, min(80, cols))
        return rows, cols
    except ValueError:
        return 20, 50

def get_speed():
    """Minta kecepatan simulasi"""
    print()
    print("  Pilih kecepatan:")
    print("  [1] Lambat (0.3s)")
    print("  [2] Normal (0.1s)")
    print("  [3] Cepat  (0.05s)")
    choice = input("  Pilihan [1-3, default=2]: ").strip()
    speeds = {'1': 0.3, '2': 0.1, '3': 0.05}
    return speeds.get(choice, 0.1)

def main():
    ROWS = 20
    COLS = 60

    while True:
        show_menu()
        choice = input("  Pilihan Anda: ").strip().upper()

        if choice == 'Q':
            clear_screen()
            print()
            print("  Terima kasih telah bermain Game of Life!")
            print()
            sys.exit(0)

        elif choice == 'C':
            ROWS, COLS = get_grid_size()
            print(f"\n  Ukuran grid diatur: {ROWS} x {COLS}")
            time.sleep(1)
            continue

        speed = get_speed()

        if choice == '1':
            grid = create_random_grid(ROWS, COLS, density=0.2)
            mode = "Acak 20%"
        elif choice == '2':
            grid = create_random_grid(ROWS, COLS, density=0.4)
            mode = "Acak 40%"
        elif choice == '3':
            grid = create_random_grid(ROWS, COLS, density=0.6)
            mode = "Acak 60%"
        elif choice == '4':
            grid = create_random_grid(ROWS, COLS, density=0.8)
            mode = "Acak 80%"
        elif choice == '5':
            grid = create_pattern_grid(ROWS, COLS, "glider")
            mode = "Glider"
        elif choice == '6':
            grid = create_pattern_grid(ROWS, COLS, "blinker")
            mode = "Blinker"
        elif choice == '7':
            grid = create_pattern_grid(ROWS, COLS, "block")
            mode = "Block"
        elif choice == '8':
            grid = create_pattern_grid(ROWS, COLS, "r_pentomino")
            mode = "R-Pentomino"
        elif choice == '9':
            grid = create_pattern_grid(ROWS, COLS, "pulsar")
            mode = "Pulsar"
        elif choice == 'A':
            grid = create_pattern_grid(ROWS, COLS, "spaceship")
            mode = "Spaceship"
        elif choice == 'B':
            grid = create_pattern_grid(ROWS, COLS, "acorn")
            mode = "Acorn"
        else:
            print("\n  Pilihan tidak valid, coba lagi...")
            time.sleep(1)
            continue

        print(f"\n  Memulai simulasi [{mode}]... Tekan Ctrl+C untuk berhenti.\n")
        time.sleep(1.5)
        run_simulation(grid, ROWS, COLS, mode, max_gen=1000, delay=speed)

        print("\n  Simulasi selesai. Kembali ke menu...")
        time.sleep(2)

if __name__ == "__main__":
    main()