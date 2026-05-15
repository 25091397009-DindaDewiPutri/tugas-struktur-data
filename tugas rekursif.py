"""
=============================================================
  TUGAS REKURSIF - Algoritma Backtracking
  1. N-Queens (N-Ratu)
  2. Knight's Tour (Tur Kuda)
  3. Knapsack (Masalah Karung)
=============================================================
"""

import sys

# ─────────────────────────────────────────────
# 1. N-QUEENS
# ─────────────────────────────────────────────

def is_safe_queen(board, row, col, n):
    """Cek apakah aman menaruh ratu di (row, col)."""
    # Cek kolom
    for i in range(row):
        if board[i] == col:
            return False
    # Cek diagonal kiri-atas
    i, j = row - 1, col - 1
    while i >= 0 and j >= 0:
        if board[i] == j:
            return False
        i -= 1; j -= 1
    # Cek diagonal kanan-atas
    i, j = row - 1, col + 1
    while i >= 0 and j < n:
        if board[i] == j:
            return False
        i -= 1; j += 1
    return True


def solve_nqueens(board, row, n, solutions):
    """Rekursif: tempatkan ratu baris per baris."""
    if row == n:
        solutions.append(board[:])   # Simpan solusi
        return
    for col in range(n):
        if is_safe_queen(board, row, col, n):
            board[row] = col
            solve_nqueens(board, row + 1, n, solutions)
            board[row] = -1          # Backtrack


def print_nqueens_board(solution, n):
    """Cetak papan N-Queens."""
    for row in range(n):
        col = solution[row]
        line = " . " * col + " Q " + " . " * (n - col - 1)
        print(line)
    print()


def run_nqueens():
    print("\n" + "="*50)
    print("  SOAL 1 — N-QUEENS (N-RATU)")
    print("="*50)
    try:
        n = int(input("Masukkan ukuran papan (N ≥ 4): "))
        if n < 4:
            print("N minimal 4.")
            return
    except ValueError:
        print("Input tidak valid.")
        return

    solutions = []
    solve_nqueens([-1] * n, 0, n, solutions)

    if not solutions:
        print(f"Tidak ada solusi untuk N={n}.")
        return

    print(f"\nDitemukan {len(solutions)} solusi untuk papan {n}×{n}.")
    print(f"Menampilkan solusi pertama:\n")
    print_nqueens_board(solutions[0], n)

    # Tampilkan semua solusi jika diminta
    try:
        show_all = input(f"Tampilkan semua {len(solutions)} solusi? (y/n): ").strip().lower()
    except EOFError:
        show_all = 'n'

    if show_all == 'y':
        for idx, sol in enumerate(solutions, 1):
            print(f"--- Solusi {idx} ---")
            print_nqueens_board(sol, n)


# ─────────────────────────────────────────────
# 2. KNIGHT'S TOUR (TUR KUDA)
# ─────────────────────────────────────────────

KNIGHT_MOVES = [(-2,-1),(-2,1),(-1,-2),(-1,2),
                (1,-2),(1,2),(2,-1),(2,1)]


def get_valid_moves(x, y, board, n):
    """Kembalikan daftar langkah valid dari posisi (x, y)."""
    moves = []
    for dx, dy in KNIGHT_MOVES:
        nx, ny = x + dx, y + dy
        if 0 <= nx < n and 0 <= ny < n and board[nx][ny] == -1:
            moves.append((nx, ny))
    return moves


def warnsdorff_degree(pos, board, n):
    """Heuristik Warnsdorff: jumlah langkah lanjutan dari pos."""
    return len(get_valid_moves(pos[0], pos[1], board, n))


def knight_tour(board, x, y, step, n):
    """Rekursif backtracking + heuristik Warnsdorff."""
    if step == n * n:
        return True     # Semua petak dikunjungi

    # Urutkan langkah berdasarkan heuristik (paling sedikit pilihan dulu)
    nexts = get_valid_moves(x, y, board, n)
    nexts.sort(key=lambda p: warnsdorff_degree(p, board, n))

    for nx, ny in nexts:
        board[nx][ny] = step
        if knight_tour(board, nx, ny, step + 1, n):
            return True
        board[nx][ny] = -1          # Backtrack

    return False


def print_kt_board(board, n):
    """Cetak papan Knight's Tour."""
    for row in board:
        print("  ".join(f"{v:2d}" for v in row))
    print()


def print_kt_steps(board, n):
    """Cetak urutan langkah kuda."""
    # Buat peta: step → (row, col)
    steps = {}
    for r in range(n):
        for c in range(n):
            steps[board[r][c]] = (r, c)
    print("Urutan langkah:")
    for s in range(n * n):
        r, c = steps[s]
        arrow = " → " if s < n * n - 1 else ""
        print(f"  Langkah {s+1:2d}: ({r}, {c}){arrow}" if s % 4 == 3 or s == n*n-1
              else f"  Langkah {s+1:2d}: ({r}, {c}){arrow}", end="")
        if (s + 1) % 4 == 0:
            print()
    print("\n")


def run_knights_tour():
    print("\n" + "="*50)
    print("  SOAL 2 — KNIGHT'S TOUR (TUR KUDA)")
    print("="*50)
    try:
        start_r = int(input("Masukkan baris awal kuda (0-7): "))
        start_c = int(input("Masukkan kolom awal kuda (0-7): "))
    except ValueError:
        print("Input tidak valid.")
        return

    n = 8
    if not (0 <= start_r < n and 0 <= start_c < n):
        print("Posisi harus antara 0 dan 7.")
        return

    board = [[-1] * n for _ in range(n)]
    board[start_r][start_c] = 0

    print(f"\nMencari jalur dari ({start_r}, {start_c})...")
    found = knight_tour(board, start_r, start_c, 1, n)

    if found:
        print(f"Jalur lengkap ditemukan!\n")
        print("Papan (angka = urutan langkah ke-):")
        print_kt_board(board, n)
        print_kt_steps(board, n)
    else:
        print("Tidak ada jalur yang ditemukan dari posisi tersebut.")


# ─────────────────────────────────────────────
# 3. KNAPSACK (MASALAH KARUNG)
# ─────────────────────────────────────────────

def knapsack(weights, target, idx, current, chosen):
    """
    Rekursif: cari kombinasi barang agar total berat = target.
    Kembalikan daftar berat barang yang dipilih, atau None jika tidak ada.
    """
    # Basis: total berat tepat sama dengan target
    if current == target:
        return chosen[:]

    # Basis: indeks habis atau sudah melebihi target
    if idx >= len(weights) or current > target:
        return None

    # Cabang 1: ambil barang ke-idx
    chosen.append(weights[idx])
    result = knapsack(weights, target, idx + 1, current + weights[idx], chosen)
    if result is not None:
        return result
    chosen.pop()            # Backtrack

    # Cabang 2: lewati barang ke-idx
    return knapsack(weights, target, idx + 1, current, chosen)


def knapsack_all(weights, target, idx, current, chosen, all_solutions):
    """Versi lanjutan: cari SEMUA kombinasi yang memenuhi target."""
    if current == target:
        all_solutions.append(chosen[:])
        return
    if idx >= len(weights) or current > target:
        return

    # Ambil barang ke-idx
    chosen.append(weights[idx])
    knapsack_all(weights, target, idx + 1, current + weights[idx], chosen, all_solutions)
    chosen.pop()

    # Lewati barang ke-idx
    knapsack_all(weights, target, idx + 1, current, chosen, all_solutions)


def run_knapsack():
    print("\n" + "="*50)
    print("  SOAL 3 — KNAPSACK (MASALAH KARUNG)")
    print("="*50)

    raw = input("Masukkan berat barang (pisahkan dengan koma), contoh: 2,5,6,9,12,14,20\n> ")
    try:
        weights = [int(x.strip()) for x in raw.split(',') if x.strip()]
    except ValueError:
        print("Input tidak valid.")
        return

    try:
        target = int(input("Masukkan berat target: "))
    except ValueError:
        print("Input tidak valid.")
        return

    if not weights or target <= 0:
        print("Data tidak valid.")
        return

    print(f"\nBarang tersedia : {weights}")
    print(f"Berat target    : {target}")
    print(f"Mencari solusi...\n")

    # Cari satu solusi
    result = knapsack(weights, target, 0, 0, [])
    if result:
        print(f"✓ Solusi ditemukan  : {result}")
        print(f"  Total berat       : {sum(result)}")
    else:
        print("✗ Tidak ada kombinasi yang totalnya tepat sama dengan target.")
        return

    # Tawarkan mencari semua solusi
    try:
        show_all = input("\nCari SEMUA kombinasi yang memenuhi? (y/n): ").strip().lower()
    except EOFError:
        show_all = 'n'

    if show_all == 'y':
        all_solutions = []
        knapsack_all(weights, target, 0, 0, [], all_solutions)
        print(f"\nDitemukan {len(all_solutions)} kombinasi:")
        for i, sol in enumerate(all_solutions, 1):
            print(f"  {i:3d}. {sol}  (total = {sum(sol)})")


# ─────────────────────────────────────────────
# MENU UTAMA
# ─────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════════════════╗")
    print("║   TUGAS REKURSIF — Algoritma Backtracking   ║")
    print("╚══════════════════════════════════════════════╝")
    print("  1. N-Queens (N-Ratu)")
    print("  2. Knight's Tour (Tur Kuda)")
    print("  3. Knapsack (Masalah Karung)")
    print("  4. Jalankan Semua (Demo)")
    print("  0. Keluar")

    try:
        pilihan = input("\nPilih nomor soal: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nKeluar.")
        sys.exit(0)

    if pilihan == '1':
        run_nqueens()
    elif pilihan == '2':
        run_knights_tour()
    elif pilihan == '3':
        run_knapsack()
    elif pilihan == '4':
        # Demo: jalankan semua dengan input default
        print("\n[Demo N-Queens N=6]")
        sols = []
        solve_nqueens([-1]*6, 0, 6, sols)
        print(f"N=6 → {len(sols)} solusi. Solusi pertama:")
        print_nqueens_board(sols[0], 6)

        print("[Demo Knight's Tour dari (0,0)]")
        b = [[-1]*8 for _ in range(8)]; b[0][0] = 0
        knight_tour(b, 0, 0, 1, 8)
        print("Papan hasil Tur Kuda:")
        print_kt_board(b, 8)

        print("[Demo Knapsack target=30, barang=[2,5,6,9,12,14,20]]")
        r = knapsack([2,5,6,9,12,14,20], 30, 0, 0, [])
        print(f"Solusi: {r}, total={sum(r)}\n")
    elif pilihan == '0':
        print("Keluar.")
        sys.exit(0)
    else:
        print("Pilihan tidak valid.")

    # Kembali ke menu
    try:
        lagi = input("\nKembali ke menu? (y/n): ").strip().lower()
        if lagi == 'y':
            main()
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()