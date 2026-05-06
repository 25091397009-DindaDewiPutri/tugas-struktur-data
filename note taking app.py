"""
========================================================================
LATIHAN SOAL — Advanced Linked Lists
Mata Kuliah: Struktur Data Lanjut

TUGAS:
    Rancang struktur data untuk aplikasi note-taking yang mendukung:
    1. Multiple tags per note   → Multi-Linked by Tag
    2. Chronological & Alpha    → Doubly Linked List (sorted)
    3. Sync status tracking     → Circular Buffer (recent changes)

PENULIS : [Nama Mahasiswa]
TANGGAL : 2024
========================================================================
"""

from datetime import datetime


# ========================================================================
# BAGIAN 1 — KONSTANTA SYNC STATUS
# ========================================================================

class SyncStatus:
    """
    Enum-like class untuk status sinkronisasi sebuah note.
    Tiga kemungkinan status:
      - PENDING : note baru dibuat/diubah, belum di-sync ke server
      - SYNCED  : note sudah berhasil di-sync ke server
      - FAILED  : percobaan sync gagal (misalnya tidak ada internet)
    """
    PENDING = "PENDING"
    SYNCED  = "SYNCED"
    FAILED  = "FAILED"


# ========================================================================
# BAGIAN 2 — NODE UTAMA (Multi-Linked Node)
# ========================================================================

class NoteNode:
    """
    Satu node merepresentasikan satu catatan (note).

    Node ini MULTI-LINKED — artinya satu node fisik yang sama
    terhubung ke beberapa chain (rantai) sekaligus:

      Chain 1 — Chronological Doubly Linked List
                (urut tanggal dibuat, oldest → newest)
      Chain 2 — Alphabetical Doubly Linked List
                (urut judul A → Z)
      Chain 3 — Tag Chains (partial chains per tag)
                setiap tag memiliki pointer nextByTag sendiri

    Keuntungan: 1 node fisik, multiple logical view.
    Hemat memori dibanding menyimpan salinan node di setiap chain.
    """

    def __init__(self, note_id, title, content, created_at):
        # ── Data Utama ──────────────────────────────────────────────────
        self.note_id    = note_id      # ID unik note (string/int)
        self.title      = title        # Judul note (string)
        self.content    = content      # Isi konten note (string)
        self.created_at = created_at   # Waktu dibuat (datetime)

        # ── Chain 1: Chronological Doubly Linked List ────────────────────
        # prevChron → node yang dibuat LEBIH LAMA
        # nextChron → node yang dibuat LEBIH BARU
        self.prevChron = None
        self.nextChron = None

        # ── Chain 2: Alphabetical Doubly Linked List ─────────────────────
        # prevAlpha → node dengan judul yang lebih kecil (sebelumnya A-Z)
        # nextAlpha → node dengan judul yang lebih besar (berikutnya A-Z)
        self.prevAlpha = None
        self.nextAlpha = None

        # ── Chain 3: Multi-Linked by Tag ─────────────────────────────────
        # nextByTag = dict {nama_tag: NoteNode_berikutnya_di_chain_tag_ini}
        # Contoh: {"python": <NoteNode B>, "work": <NoteNode C>}
        self.nextByTag = {}

        # Daftar tag yang dimiliki note ini (untuk keperluan delete)
        self.tags = []

        # ── Sync Status ──────────────────────────────────────────────────
        self.sync_status = SyncStatus.PENDING

    def __repr__(self):
        return (f"NoteNode(id={self.note_id!r}, title={self.title!r}, "
                f"tags={self.tags}, sync={self.sync_status})")


# ========================================================================
# BAGIAN 3 — TAG CHAIN (Partial Chain per Tag)
# ========================================================================

class TagChain:
    """
    Satu TagChain merepresentasikan chain untuk SATU tag tertentu.

    Ini adalah PARTIAL CHAIN — hanya berisi note yang memiliki tag ini.
    Misalnya, TagChain("python") hanya menghubungkan note-note bertag "python".

    Setiap note yang punya tag ini dihubungkan lewat:
        node.nextByTag["python"] → node berikutnya di chain python

    Insert di depan: O(1)
    Traverse seluruh chain: O(k), k = jumlah note dengan tag ini
    """

    def __init__(self, tag_name):
        self.tag_name = tag_name   # Nama tag (string)
        self.head     = None       # NoteNode pertama di chain ini
        self.count    = 0          # Jumlah note dalam chain ini

    def insert(self, new_node):
        """
        Sisipkan note baru di depan chain tag ini.
        Kompleksitas: O(1)
        """
        # Hubungkan new_node ke head saat ini
        new_node.nextByTag[self.tag_name] = self.head
        # Update head menjadi new_node
        self.head = new_node
        self.count += 1

        # Daftarkan tag ke list tags milik node
        if self.tag_name not in new_node.tags:
            new_node.tags.append(self.tag_name)

    def remove(self, target_node):
        """
        Hapus node tertentu dari chain tag ini.
        Kompleksitas: O(k), k = jumlah node dalam chain
        """
        prev = None
        cur  = self.head

        # Cari posisi target_node di chain
        while cur is not None and cur is not target_node:
            prev = cur
            cur  = cur.nextByTag.get(self.tag_name)

        if cur is None:
            return  # Node tidak ditemukan di chain ini

        # Bypass node yang ingin dihapus
        nxt = cur.nextByTag.get(self.tag_name)
        if prev is None:
            self.head = nxt          # Hapus head
        else:
            prev.nextByTag[self.tag_name] = nxt

        # Bersihkan pointer tag dari node yang dihapus
        cur.nextByTag.pop(self.tag_name, None)
        if self.tag_name in cur.tags:
            cur.tags.remove(self.tag_name)

        self.count -= 1

    def traverse(self):
        """
        Generator: iterasi semua note dalam chain ini.
        Kompleksitas: O(k)
        """
        cur = self.head
        while cur is not None:
            yield cur
            cur = cur.nextByTag.get(self.tag_name)

    def __repr__(self):
        return f"TagChain(tag={self.tag_name!r}, count={self.count})"


# ========================================================================
# BAGIAN 4 — CIRCULAR BUFFER (Sync Status Tracking)
# ========================================================================

class CircularBuffer:
    """
    Circular Buffer untuk melacak recent changes (perubahan terbaru).

    Cara kerja:
      - Buffer berukuran tetap (capacity).
      - Setiap perubahan sync ditulis di posisi 'tail'.
      - Ketika buffer penuh, entry TERLAMA otomatis tertimpa (overwrite).
      - Tidak ada NULL terminator — gunakan pointer head & tail.

    Operasi:
      write(event) → O(1)   tambah event baru
      read_all()   → O(N)   baca semua event dari oldest ke newest
    """

    def __init__(self, capacity=10):
        self.capacity = capacity
        self._buffer  = [None] * capacity   # Array statis ukuran tetap
        self._head    = 0     # Index entry paling lama (untuk baca)
        self._tail    = 0     # Index posisi tulis berikutnya
        self._count   = 0     # Jumlah entry aktif saat ini

    def write(self, note_node, status):
        """
        Catat event sync ke buffer.
        Jika penuh, entry terlama tertimpa (head maju).
        Kompleksitas: O(1)
        """
        # Simpan event sebagai tuple (node, status, timestamp)
        event = {
            "note_id"   : note_node.note_id,
            "title"     : note_node.title,
            "status"    : status,
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._buffer[self._tail] = event
        self._tail = (self._tail + 1) % self.capacity   # Wrap around

        if self._count < self.capacity:
            self._count += 1
        else:
            # Buffer penuh → geser head (oldest terhapus otomatis)
            self._head = (self._head + 1) % self.capacity

    def read_all(self):
        """
        Kembalikan semua event dari oldest → newest.
        Kompleksitas: O(N), N = jumlah entry aktif
        """
        result = []
        for i in range(self._count):
            idx = (self._head + i) % self.capacity
            result.append(self._buffer[idx])
        return result

    def is_empty(self):
        return self._count == 0

    def is_full(self):
        return self._count == self.capacity

    def __repr__(self):
        return (f"CircularBuffer(capacity={self.capacity}, "
                f"count={self._count})")


# ========================================================================
# BAGIAN 5 — NOTEBOOK (Controller Utama)
# ========================================================================

class NoteBook:
    """
    Controller utama yang mengelola SEMUA struktur data:

      1. Chronological DLL  : headChron ↔ ... ↔ tailChron
         Sorted by created_at ascending (oldest di depan)

      2. Alphabetical DLL   : headAlpha ↔ ... ↔ tailAlpha
         Sorted by title ascending (A di depan)

      3. Tag Registry       : dict {tag_name → TagChain}
         Setiap tag punya chain sendiri (partial multi-linked)

      4. Circular Buffer    : melacak N perubahan sync terakhir

    PENTING (dari materi DLL):
      - Selalu update SEMUA chain saat insert maupun delete.
      - Delete dari semua chain SEBELUM dealokasi node.
    """

    def __init__(self, buffer_size=10):
        # ── Chronological DLL ────────────────────────────────────────────
        self.headChron = None   # Note paling lama
        self.tailChron = None   # Note paling baru

        # ── Alphabetical DLL ─────────────────────────────────────────────
        self.headAlpha = None   # Judul paling awal (A)
        self.tailAlpha = None   # Judul paling akhir (Z)

        # ── Tag Registry ─────────────────────────────────────────────────
        self.tag_chains = {}    # {tag_name: TagChain}

        # ── Circular Buffer ──────────────────────────────────────────────
        self.sync_buffer = CircularBuffer(capacity=buffer_size)

        # ── Counter ──────────────────────────────────────────────────────
        self._num_notes = 0

    # ────────────────────────────────────────────────────────────────────
    # OPERASI INSERT
    # ────────────────────────────────────────────────────────────────────

    def add_note(self, note_id, title, content, created_at, tags=None):
        """
        Tambah note baru ke SEMUA chain sekaligus.
        Kompleksitas: O(n) untuk insert sorted ke 2 DLL.

        Parameter:
          note_id    : ID unik (string/int)
          title      : Judul note
          content    : Isi note
          created_at : datetime kapan note dibuat
          tags       : list string tag (opsional)
        """
        if tags is None:
            tags = []

        new_node = NoteNode(note_id, title, content, created_at)
        self._num_notes += 1

        # Sisipkan ke Chronological DLL (sorted by created_at)
        self._insert_chron(new_node)

        # Sisipkan ke Alphabetical DLL (sorted by title)
        self._insert_alpha(new_node)

        # Daftarkan ke setiap TagChain
        for tag in tags:
            if tag not in self.tag_chains:
                self.tag_chains[tag] = TagChain(tag)
            self.tag_chains[tag].insert(new_node)

        # Catat ke circular buffer sebagai PENDING
        self.sync_buffer.write(new_node, SyncStatus.PENDING)

        return new_node

    def _insert_chron(self, new_node):
        """
        Sisipkan node ke Chronological DLL secara sorted.
        Mirip implementasi insertSorted dari materi slide 14.
        Kompleksitas: O(n)
        """
        # Kasus 1: List kosong
        if self.headChron is None:
            self.headChron = self.tailChron = new_node
            return

        # Kasus 2: Insert di depan (lebih lama dari semua)
        if new_node.created_at <= self.headChron.created_at:
            new_node.nextChron        = self.headChron
            self.headChron.prevChron  = new_node
            self.headChron            = new_node
            return

        # Kasus 3: Insert di belakang (paling baru)
        if new_node.created_at >= self.tailChron.created_at:
            new_node.prevChron        = self.tailChron
            self.tailChron.nextChron  = new_node
            self.tailChron            = new_node
            return

        # Kasus 4: Insert di tengah — cari posisi yang tepat
        cur = self.headChron
        while cur is not None and cur.created_at < new_node.created_at:
            cur = cur.nextChron

        # Sisipkan new_node sebelum cur
        new_node.nextChron       = cur
        new_node.prevChron       = cur.prevChron
        cur.prevChron.nextChron  = new_node
        cur.prevChron            = new_node

    def _insert_alpha(self, new_node):
        """
        Sisipkan node ke Alphabetical DLL secara sorted.
        Sama logikanya dengan _insert_chron tapi pakai title.
        Kompleksitas: O(n)
        """
        # Kasus 1: List kosong
        if self.headAlpha is None:
            self.headAlpha = self.tailAlpha = new_node
            return

        # Kasus 2: Insert di depan
        if new_node.title <= self.headAlpha.title:
            new_node.nextAlpha        = self.headAlpha
            self.headAlpha.prevAlpha  = new_node
            self.headAlpha            = new_node
            return

        # Kasus 3: Insert di belakang
        if new_node.title >= self.tailAlpha.title:
            new_node.prevAlpha        = self.tailAlpha
            self.tailAlpha.nextAlpha  = new_node
            self.tailAlpha            = new_node
            return

        # Kasus 4: Insert di tengah
        cur = self.headAlpha
        while cur is not None and cur.title < new_node.title:
            cur = cur.nextAlpha

        new_node.nextAlpha       = cur
        new_node.prevAlpha       = cur.prevAlpha
        cur.prevAlpha.nextAlpha  = new_node
        cur.prevAlpha            = new_node

    # ────────────────────────────────────────────────────────────────────
    # OPERASI DELETE
    # ────────────────────────────────────────────────────────────────────

    def remove_note(self, node):
        """
        Hapus note dari SEMUA chain sebelum dealokasi.
        (Prinsip dari materi: delete dari semua chain lebih dulu)

        Kompleksitas:
          - Chron DLL: O(1) karena punya prev & next
          - Alpha DLL: O(1) karena punya prev & next
          - Tag chains: O(k * T), k=panjang chain, T=jumlah tag
        """
        # ── Hapus dari Chronological DLL ─────────────────────────────────
        if node.prevChron:
            node.prevChron.nextChron = node.nextChron
        else:
            self.headChron = node.nextChron   # Node adalah head

        if node.nextChron:
            node.nextChron.prevChron = node.prevChron
        else:
            self.tailChron = node.prevChron   # Node adalah tail

        # ── Hapus dari Alphabetical DLL ──────────────────────────────────
        if node.prevAlpha:
            node.prevAlpha.nextAlpha = node.nextAlpha
        else:
            self.headAlpha = node.nextAlpha

        if node.nextAlpha:
            node.nextAlpha.prevAlpha = node.prevAlpha
        else:
            self.tailAlpha = node.prevAlpha

        # ── Hapus dari setiap Tag Chain ───────────────────────────────────
        # Buat salinan list tags dulu karena TagChain.remove() akan
        # memodifikasi node.tags saat iterasi
        tags_copy = list(node.tags)
        for tag in tags_copy:
            if tag in self.tag_chains:
                self.tag_chains[tag].remove(node)

        self._num_notes -= 1
        print(f"  [DELETE] Note '{node.title}' dihapus dari semua chain.")

    # ────────────────────────────────────────────────────────────────────
    # OPERASI SYNC STATUS
    # ────────────────────────────────────────────────────────────────────

    def update_sync(self, node, status):
        """
        Update status sync sebuah note dan catat ke circular buffer.
        Kompleksitas: O(1)
        """
        node.sync_status = status
        self.sync_buffer.write(node, status)
        print(f"  [SYNC] '{node.title}' → {status}")

    # ────────────────────────────────────────────────────────────────────
    # VIEW / TRAVERSAL
    # ────────────────────────────────────────────────────────────────────

    def view_chronological(self, reverse=False):
        """
        Tampilkan semua note urut tanggal.
        reverse=False → oldest first (forward traversal)
        reverse=True  → newest first (reverse traversal via .prevChron)
        Kompleksitas: O(n)
        """
        results = []
        if not reverse:
            cur = self.headChron
            while cur:
                results.append(cur)
                cur = cur.nextChron
        else:
            cur = self.tailChron
            while cur:
                results.append(cur)
                cur = cur.prevChron
        return results

    def view_alphabetical(self, reverse=False):
        """
        Tampilkan semua note urut judul A-Z atau Z-A.
        Kompleksitas: O(n)
        """
        results = []
        if not reverse:
            cur = self.headAlpha
            while cur:
                results.append(cur)
                cur = cur.nextAlpha
        else:
            cur = self.tailAlpha
            while cur:
                results.append(cur)
                cur = cur.prevAlpha
        return results

    def view_by_tag(self, tag_name):
        """
        Tampilkan semua note yang memiliki tag tertentu.
        Kompleksitas: O(k), k = jumlah note dengan tag tersebut
        """
        chain = self.tag_chains.get(tag_name)
        if chain is None:
            return []
        return list(chain.traverse())

    def get_recent_changes(self):
        """
        Ambil semua entry dari circular buffer (oldest → newest).
        Kompleksitas: O(N_buf)
        """
        return self.sync_buffer.read_all()

    def num_notes(self):
        return self._num_notes

    def __repr__(self):
        return (f"NoteBook(notes={self._num_notes}, "
                f"tags={list(self.tag_chains.keys())}, "
                f"buffer={self.sync_buffer})")


# ========================================================================
# BAGIAN 6 — FUNGSI HELPER UNTUK DEMO
# ========================================================================

def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def print_notes(notes, label=""):
    if label:
        print(f"\n  {label}:")
    if not notes:
        print("    (kosong)")
        return
    for n in notes:
        print(f"    [{n.created_at.strftime('%Y-%m-%d')}] "
              f"{n.title:<25} tags={n.tags}  sync={n.sync_status}")

def print_sync_log(events, label="Recent Sync Events"):
    print(f"\n  {label}:")
    if not events:
        print("    (buffer kosong)")
        return
    for i, e in enumerate(events, 1):
        print(f"    {i}. [{e['timestamp']}] "
              f"{e['title']:<25} → {e['status']}")


# ========================================================================
# BAGIAN 7 — DEMO / PENGUJIAN
# ========================================================================

if __name__ == "__main__":

    print_separator("DEMO APLIKASI NOTE-TAKING — ADVANCED LINKED LISTS")

    # ── Inisialisasi NoteBook ────────────────────────────────────────────
    nb = NoteBook(buffer_size=5)

    # ── Tambah Note ──────────────────────────────────────────────────────
    print_separator("1. MENAMBAHKAN NOTE")

    n1 = nb.add_note("n1", "Belajar Python",
                     "Materi dasar Python: variabel, loop, fungsi",
                     datetime(2024, 1, 1, 9, 0),
                     tags=["python", "study", "programming"])

    n2 = nb.add_note("n2", "Meeting Notes",
                     "Hasil meeting sprint planning Q1 2024",
                     datetime(2024, 1, 5, 14, 30),
                     tags=["work", "meeting"])

    n3 = nb.add_note("n3", "Todo List Harian",
                     "Daftar tugas: makan, olahraga, belajar DS",
                     datetime(2024, 1, 3, 8, 0),
                     tags=["todo", "daily"])

    n4 = nb.add_note("n4", "Algoritma Sorting",
                     "Bubble sort, merge sort, quick sort",
                     datetime(2024, 1, 7, 16, 0),
                     tags=["python", "study", "algorithm"])

    n5 = nb.add_note("n5", "Resep Kue Coklat",
                     "Bahan: tepung, gula, coklat bubuk...",
                     datetime(2024, 1, 2, 10, 0),
                     tags=["personal", "cooking"])

    print(f"\n  Total note: {nb.num_notes()}")

    # ── View Chronological ───────────────────────────────────────────────
    print_separator("2. VIEW CHRONOLOGICAL (Doubly Linked List)")

    notes_chron = nb.view_chronological(reverse=False)
    print_notes(notes_chron, "Oldest → Newest (forward via nextChron)")

    notes_chron_rev = nb.view_chronological(reverse=True)
    print_notes(notes_chron_rev, "Newest → Oldest (reverse via prevChron)")

    # ── View Alphabetical ────────────────────────────────────────────────
    print_separator("3. VIEW ALPHABETICAL (Doubly Linked List)")

    notes_alpha = nb.view_alphabetical(reverse=False)
    print_notes(notes_alpha, "A → Z (forward via nextAlpha)")

    notes_alpha_rev = nb.view_alphabetical(reverse=True)
    print_notes(notes_alpha_rev, "Z → A (reverse via prevAlpha)")

    # ── View by Tag ──────────────────────────────────────────────────────
    print_separator("4. VIEW BY TAG (Multi-Linked Chains)")

    for tag in ["python", "study", "work", "todo", "personal"]:
        notes_tag = nb.view_by_tag(tag)
        titles = [n.title for n in notes_tag]
        print(f"  #{tag:<15} → {titles}")

    # ── Sync Status Tracking ─────────────────────────────────────────────
    print_separator("5. SYNC STATUS TRACKING (Circular Buffer)")

    print("\n  Update sync status beberapa note:")
    nb.update_sync(n1, SyncStatus.SYNCED)
    nb.update_sync(n2, SyncStatus.SYNCED)
    nb.update_sync(n3, SyncStatus.FAILED)
    nb.update_sync(n4, SyncStatus.PENDING)
    nb.update_sync(n5, SyncStatus.SYNCED)   # Buffer penuh, oldest ditimpa
    nb.update_sync(n3, SyncStatus.SYNCED)   # Retry n3 yang gagal

    events = nb.get_recent_changes()
    print_sync_log(events, "Isi Circular Buffer (5 terbaru)")

    # ── Operasi Delete ───────────────────────────────────────────────────
    print_separator("6. DELETE NOTE (Hapus dari SEMUA chain)")

    print(f"\n  Sebelum delete: {nb.num_notes()} note")
    nb.remove_note(n3)
    print(f"  Sesudah delete: {nb.num_notes()} note")

    notes_after = nb.view_chronological()
    print_notes(notes_after, "Chronological setelah delete")

    # Verifikasi tag chain juga terupdate
    print(f"\n  Tag #todo setelah delete n3: "
          f"{[n.title for n in nb.view_by_tag('todo')]}")

    # ── Ringkasan Kompleksitas ───────────────────────────────────────────
    print_separator("7. RINGKASAN KOMPLEKSITAS OPERASI")

    kompleksitas = [
        ("add_note (insert sorted ke 2 DLL)", "O(n)"),
        ("remove_note (dari 2 DLL + T tag chain)", "O(k·T)"),
        ("view_chronological / view_alphabetical", "O(n)"),
        ("Reverse traversal (via .prev pointer)", "O(n)"),
        ("view_by_tag (traverse 1 tag chain)", "O(k)"),
        ("sync_buffer.write (circular buffer)", "O(1)"),
        ("sync_buffer.read_all", "O(N_buf)"),
        ("Memori total", "O(N · T)"),
    ]

    print()
    for operasi, kompleks in kompleksitas:
        print(f"  {operasi:<50} → {kompleks}")

    print_separator("SELESAI")
    print("  Semua fitur berhasil didemonstrasikan:")
    print("  ✓ Multi-Linked by Tag")
    print("  ✓ Doubly Linked Chronological (sorted)")
    print("  ✓ Doubly Linked Alphabetical (sorted)")
    print("  ✓ Circular Buffer Sync Tracking")
    print()