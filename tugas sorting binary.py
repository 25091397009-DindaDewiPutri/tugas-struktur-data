"""
=============================================================================
JAWABAN LENGKAP: Advanced Sorting & Binary Tree / Heap
=============================================================================

BAGIAN A - TEORI (ada di docstring masing-masing fungsi & komentar inline)
BAGIAN B - IMPLEMENTASI KODE PYTHON

=============================================================================
"""

import math
from typing import List, Optional
from collections import deque


# ============================================================================
# MODUL 1: AdvancedSorter  (Jawaban Soal Sorting Lanjutan)
# ============================================================================

class ListNode:
    def __init__(self, data, next=None):
        self.data = data
        self.next = next

    def __repr__(self):
        return f"ListNode({self.data})"


class AdvancedSorter:
    """
    =========================================================================
    JAWABAN TEORI (soal a, b, c, d dari tugas sorting):
    =========================================================================

    a. RADIX SORT & MEMORI O(1):
    -----------------------------------------------------------------------
    Radix Sort standar (array of 10 queues) TIDAK memenuhi O(1) karena:
      - Membuat 10 Queue terpisah di luar array input.
      - Total kapasitas queue = O(n) (semua n elemen bisa masuk ke satu bin).
      - Queue itu sendiri adalah linked list → setiap node = O(1) overhead,
        tapi total n node = O(n) memori EKSTRA di luar input array.
      → Ruang tambahan = O(n + k) dengan k = 10 (jumlah bin), bukan O(1).

    Improved Merge Sort (Listing 12.2 & 12.4):
      - Mengalokasi SATU tmpArray berukuran n SEKALI di awal (wrapper).
      - Semua panggilan rekursif _merge_virtual berbagi tmpArray yang sama.
      - Tidak ada array/list baru yang dibuat di setiap rekursi.
      - Versi slice membuat sublist baru O(n/2) di SETIAP level → total
        overhead O(n log n) ruang, sangat boros.
      → tmpArray tunggal = O(n) total, tapi FIXED, tidak bertambah.

    Jika ingin Radix Sort dengan O(1) memori tambahan:
      - Strategi: American Flag Sort (in-place radix sort).
        Gunakan counting array ukuran 10 (k=10 = konstan = O(1)).
        Lakukan permutasi in-place menggunakan cycle leader / two-pointer.
      - Dampak waktu: tetap O(dn) tapi konstanta membesar karena swap mahal.
      - Atau: In-Place MSD Radix Sort dengan partisi seperti quicksort.

    b. LINKED LIST SPLIT & MERGE:
    -----------------------------------------------------------------------
    _splitLinkedList() — Fast-Slow Pointer:
      - midPoint bergerak 1 langkah, curNode bergerak 2 langkah per iterasi.
      - Ketika curNode == None, midPoint tepat di tengah list.
      - Ini equivalent menghitung panjang tanpa menghitung eksplisit.
      - Kompleksitas: O(n) satu traversal saja.

    _mergeLinkedLists() dengan dummy node & tail reference:
      - Dummy node menghilangkan pengecekan "apakah list baru kosong?" 
        saat append node pertama → tidak perlu if-else khusus.
      - tail reference memastikan append O(1) (tanpa traversal ke ekor).
      - Tidak ada node baru dialokasi: hanya pointer .next yang diubah.
      - Ruang rekursi: O(log n) karena kedalaman rekursi = log n level.

    c. QUICKSORT WORST-CASE & PIVOT:
    -----------------------------------------------------------------------
    Data terurut descending + pivot = elemen pertama:
      - partitionSeq(): left selalu stuck di posisi pertama, right traverses
        seluruh array → pivot selalu jatuh di posisi paling kanan / kiri.
      - Partisi menghasilkan L = [] (kosong) dan G = n-1 elemen, atau sebaliknya.
      - Kedalaman rekursi = n (linear, bukan logaritmik).
      - Waktu = T(n) = T(n-1) + O(n) → T(n) = O(n²).

    Strategi pivot robust: Median-of-Three
      - Ambil arr[first], arr[mid], arr[last], pilih nilai tengah (median).
      - Untuk data terurut ascending/descending, pivot = elemen tengah 
        → partisi seimbang O(n/2) vs O(n/2) → T(n) = O(n log n).
      - Untuk linked list: akses arr[mid] butuh O(n) traversal (tidak ada
        random access), sehingga median-of-three mahal di LL.
      - Alternatif untuk LL: pivot = elemen pertama + gunakan fallback 
        ke merge sort jika kedalaman rekursi > 2*log2(n).

    d. BATAS TEORETIS:
    -----------------------------------------------------------------------
    Tidak kontradiktif karena:
      - Batas Ω(n log n) berlaku HANYA untuk comparison sort (yang menggunakan
        perbandingan <, >, = antar elemen sebagai satu-satunya operasi).
      - Radix sort BUKAN comparison sort: ia mengakses digit/komponen kunci
        secara langsung, bukan membandingkan dua kunci utuh.

    Dua asumsi implisit domain kunci yang membuat Radix Sort "melampaui":
      1. d (jumlah digit/komponen) adalah KONSTAN atau sangat kecil (d << n).
         Jika d = O(log n), maka O(dn) = O(n log n), tidak lebih cepat.
      2. k (ukuran alfabet / nilai tiap komponen) juga KONSTAN (mis. k=10
         untuk desimal, k=26 untuk huruf). Jika k besar, overhead O(k) 
         per iterasi menjadi signifikan.

    Asumsi ini sering tidak berlaku umum, sehingga Radix Sort tidak 
    menggantikan comparison sort untuk kasus umum.
    =========================================================================
    """

    def __init__(self):
        pass

    # =========================================================================
    # 1. ARRAY MERGE SORT (Virtual Sublists + Single tmpArray)
    # =========================================================================

    def sort_array(self, arr: List[int]) -> List[int]:
        """
        Merge sort untuk array menggunakan SATU tmpArray statis.
        Ruang ekstra: O(n) — hanya satu array sementara, tidak bertambah per rekursi.
        Waktu: O(n log n) — n elemen × log n level rekursi.
        """
        if len(arr) <= 1:
            return arr
        tmp_array = [0] * len(arr)  # Alokasi SEKALI, dipakai bersama seluruh rekursi
        self._rec_merge_sort(arr, 0, len(arr) - 1, tmp_array)
        return arr

    def _rec_merge_sort(self, arr: List[int], first: int, last: int, tmp_array: List[int]):
        """
        Rekursif merge sort dengan virtual sublist (index markers, bukan slice).
        Tidak membuat array baru → tidak ada overhead O(n) per level.
        """
        if first >= last:
            return
        mid = (first + last) // 2
        self._rec_merge_sort(arr, first, mid, tmp_array)
        self._rec_merge_sort(arr, mid + 1, last, tmp_array)
        self._merge_virtual(arr, first, mid, last, tmp_array)

    def _merge_virtual(self, arr: List[int], left_start: int, mid: int,
                       right_end: int, tmp_array: List[int]):
        """
        Menggabungkan dua virtual sublist: arr[left_start..mid] dan arr[mid+1..right_end].

        KUNCI STABILITAS: gunakan arr[a] <= arr[b] (bukan <) agar elemen
        dari sublist KIRI diambil lebih dulu ketika nilainya SAMA.
        Ini memastikan relative order elemen bernilai sama tetap terjaga.

        Langkah:
          1. Merge ke tmp_array (ruang sementara).
          2. Salin kembali ke arr[left_start..right_end].
        """
        a = left_start        # pointer sublist kiri
        b = mid + 1           # pointer sublist kanan
        m = 0                 # pointer ke tmp_array

        # Merge sampai salah satu sublist habis
        while a <= mid and b <= right_end:
            if arr[a] <= arr[b]:   # '<=' → STABLE: kiri lebih dulu jika sama
                tmp_array[m] = arr[a]
                a += 1
            else:
                tmp_array[m] = arr[b]
                b += 1
            m += 1

        # Sisa sublist kiri (jika ada)
        while a <= mid:
            tmp_array[m] = arr[a]
            a += 1
            m += 1

        # Sisa sublist kanan (jika ada)
        while b <= right_end:
            tmp_array[m] = arr[b]
            b += 1
            m += 1

        # Salin kembali ke arr
        for i in range(right_end - left_start + 1):
            arr[left_start + i] = tmp_array[i]

    # =========================================================================
    # 2. LINKED LIST MERGE SORT (Fast-Slow Pointer + Dummy Merge)
    # =========================================================================

    def sort_linked_list(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """
        Merge sort untuk singly linked list.

        Keunggulan vs array:
          - Tidak butuh tmpArray (pointer digeser, bukan data disalin).
          - Ruang ekstra: O(log n) hanya untuk stack rekursi.
          - Stable: kondisi <= di merge menjamin stabilitas.

        Dilarang alokasi node baru selama sorting (kecuali 1 dummy per merge).
        """
        # Base case: 0 atau 1 node → sudah terurut
        if head is None or head.next is None:
            return head

        # Split list menjadi dua bagian
        right_head = self._split_linked_list(head)
        left_head = head

        # Rekursif urutkan dua bagian
        left_sorted = self.sort_linked_list(left_head)
        right_sorted = self.sort_linked_list(right_head)

        # Merge dua list terurut
        return self._merge_linked_lists(left_sorted, right_sorted)

    def _split_linked_list(self, head: ListNode) -> Optional[ListNode]:
        """
        Menemukan titik tengah linked list menggunakan FAST-SLOW POINTER
        dalam SATU traversal tanpa menghitung panjang list terlebih dahulu.

        Mekanisme:
          - midPoint bergerak 1 langkah per iterasi (slow pointer).
          - curNode bergerak 2 langkah per iterasi (fast pointer).
          - Ketika curNode jatuh ke None, midPoint berada di tengah.

        Mengapa benar:
          Jika panjang list = n, curNode menempuh 2k langkah saat midPoint
          menempuh k langkah. Loop berhenti saat curNode = None (langkah ke-n).
          Maka midPoint berada di langkah ke-n/2 = titik tengah.

        Tidak ada node baru dialokasi; hanya link yang diputus.
        """
        # Inisialisasi: midPoint = node ke-1, curNode = node ke-2
        midPoint = head
        curNode = head.next

        # Loop: curNode maju 2 langkah, midPoint maju 1 langkah
        while curNode is not None and curNode.next is not None:
            midPoint = midPoint.next
            curNode = curNode.next.next

        # midPoint kini di node TERAKHIR sublist kiri
        right_head = midPoint.next   # head sublist kanan
        midPoint.next = None         # putus link → dua sublist terpisah

        return right_head

    def _merge_linked_lists(self, listA: Optional[ListNode],
                            listB: Optional[ListNode]) -> Optional[ListNode]:
        """
        Menggabungkan dua sorted linked list menggunakan DUMMY NODE & TAIL REFERENCE.

        DUMMY NODE:
          - Menghilangkan kasus khusus "list hasil masih kosong saat tambah node pertama".
          - Tanpa dummy: perlu if-else → kode lebih rumit.
          - Dengan dummy: tail.next = node baru selalu valid.

        TAIL REFERENCE:
          - Append O(1) ke ekor list hasil (tanpa traversal O(n) ke ekor).

        TIDAK ADA ALOKASI NODE BARU:
          - Hanya memodifikasi pointer .next dari node yang sudah ada.
          - Dummy node = 1 node sementara (dibuang setelah merge, di luar spec "no new node").

        STABLE: kondisi listA.data <= listB.data → ambil kiri lebih dulu jika sama.
        """
        # 1 dummy node sementara sebagai anchor
        dummy = ListNode(0)
        tail = dummy

        # Merge selama kedua list masih punya node
        while listA is not None and listB is not None:
            if listA.data <= listB.data:   # STABLE: ambil kiri jika sama
                tail.next = listA
                listA = listA.next
            else:
                tail.next = listB
                listB = listB.next
            tail = tail.next
            tail.next = None  # Putus link sisa agar list bersih

        # Sambungkan sisa list yang belum habis (O(1), tanpa traversal)
        if listA is not None:
            tail.next = listA
        else:
            tail.next = listB

        return dummy.next  # Lewati dummy node, kembalikan head asli

    # =========================================================================
    # 3. QUICK SORT dengan MEDIAN-OF-THREE PIVOT
    # =========================================================================

    def quick_sort(self, arr: List[int]) -> List[int]:
        """
        Wrapper quicksort dengan fallback ke merge sort jika kedalaman > 2*log2(n).
        Mencegah O(n²) pada data terurut/hampir terurut.
        """
        if len(arr) <= 1:
            return arr
        max_depth = int(2 * math.log2(len(arr))) if len(arr) > 1 else 1
        self._rec_quick_sort(arr, 0, len(arr) - 1, max_depth, 0)
        return arr

    def _rec_quick_sort(self, arr: List[int], first: int, last: int,
                        max_depth: int, depth: int):
        """
        Rekursif quicksort dengan depth limiter.
        Jika depth > max_depth → fallback ke merge sort untuk subarray ini.
        """
        if first >= last:
            return

        # FALLBACK: jika rekursi terlalu dalam, pakai merge sort
        if depth > max_depth:
            sub = arr[first:last + 1]
            self.sort_array(sub)
            arr[first:last + 1] = sub
            return

        # Partition dengan median-of-three pivot
        pos = self.partition_quick(arr, first, last)

        # Rekursif dua segmen
        self._rec_quick_sort(arr, first, pos - 1, max_depth, depth + 1)
        self._rec_quick_sort(arr, pos + 1, last, max_depth, depth + 1)

    def partition_quick(self, arr: List[int], first: int, last: int) -> int:
        """
        Partisi dengan MEDIAN-OF-THREE PIVOT untuk menghindari O(n²) worst-case.

        Mengapa median-of-three lebih baik dari pivot = elemen pertama:
          - Data terurut descending + pivot pertama → L selalu kosong, G = n-1 elemen.
          - Kedalaman rekursi = n, waktu = O(n²).
          - Median-of-three: ambil tengah dari arr[first], arr[mid], arr[last].
            Untuk data sorted/reverse-sorted, median ≈ nilai tengah 
            → partisi seimbang → kedalaman rekursi = O(log n).

        Langkah:
          1. Hitung mid = (first + last) // 2.
          2. Sort tiga elemen (first, mid, last) secara in-place.
          3. Tukar median ke posisi first → pivot standar.
          4. Jalankan partisi standar (Listing 12.5).

        CATATAN STABILITAS:
          Quicksort secara inherent TIDAK STABIL karena swap jarak jauh
          bisa mengubah relative order elemen bernilai sama.
          Untuk stabilitas wajib → gunakan merge sort.
        """
        mid = (first + last) // 2

        # ---- Langkah 1: Urutkan tiga kandidat pivot ----
        # Pastikan arr[first] <= arr[mid] <= arr[last]
        if arr[first] > arr[mid]:
            arr[first], arr[mid] = arr[mid], arr[first]
        if arr[first] > arr[last]:
            arr[first], arr[last] = arr[last], arr[first]
        if arr[mid] > arr[last]:
            arr[mid], arr[last] = arr[last], arr[mid]

        # arr[mid] sekarang = median → tukar ke posisi first sebagai pivot
        arr[first], arr[mid] = arr[mid], arr[first]

        # ---- Langkah 2: Partisi standar (Listing 12.5) ----
        pivot = arr[first]
        left = first + 1
        right = last

        while left <= right:
            # Geser left ke kanan sampai ketemu elemen >= pivot
            while left <= right and arr[left] < pivot:
                left += 1
            # Geser right ke kiri sampai ketemu elemen <= pivot
            while right >= left and arr[right] >= pivot:
                right -= 1
            # Swap jika belum silang
            if left < right:
                arr[left], arr[right] = arr[right], arr[left]

        # Letakkan pivot di posisi finalnya
        if right != first:
            arr[first], arr[right] = arr[right], arr[first]

        return right


# ============================================================================
# MODUL 2: ExprHeapSorter (Jawaban Soal Binary Tree & Heap)
# ============================================================================

class ExprHeapSorter:
    """
    =========================================================================
    JAWABAN TEORI (soal a, b, c, d dari tugas binary tree):
    =========================================================================

    a. POHON EKSPRESI & TRAVERSAL:
    -----------------------------------------------------------------------
    Langkah _buildTree() untuk ((8 * 5) + (9 / (7 - 4))):

    Token queue: ( ( 8 * 5 ) + ( 9 / ( 7 - 4 ) ) )

    1. Dequeue '(' → buat node kiri, rekursi ke kiri
    2.   Dequeue '(' → buat node kiri, rekursi ke kiri
    3.     Dequeue '8' → node.val = 8, return (leaf)
    4.   Dequeue '*' → node.val = '*', buat node kanan, rekursi ke kanan
    5.     Dequeue '5' → node.val = 5, return (leaf)
    6.   Dequeue ')' → diabaikan, return subtree (8*5)
    7. Dequeue '+' → node.val = '+', buat node kanan, rekursi ke kanan
    8.   Dequeue '(' → buat node kiri, rekursi ke kiri
    9.     Dequeue '9' → node.val = 9, return (leaf)
    10.  Dequeue '/' → node.val = '/', buat node kanan, rekursi ke kanan
    11.    Dequeue '(' → buat node kiri, rekursi ke kiri
    12.      Dequeue '7' → node.val = 7, return (leaf)
    13.    Dequeue '-' → node.val = '-', buat node kanan, rekursi
    14.      Dequeue '4' → node.val = 4, return (leaf)
    15.    Dequeue ')' → diabaikan, return subtree (7-4)
    16.  Dequeue ')' → diabaikan, return subtree 9/(7-4)
    17. Dequeue ')' → diabaikan, return root

    Pohon final:
              +
            /   \
           *     /
          / \   / \
         8   5 9   -
                  / \
                 7   4

    Postorder → Notasi Postfix:
      - Postorder: kunjungi kiri → kanan → node.
      - Setiap operator muncul SETELAH kedua operandnya → valid postfix.
      - Tidak perlu tanda kurung karena urutan evaluasi sudah implisit di struktur pohon.

    Inorder → Memerlukan Tanda Kurung (Listing 13.7):
      - Inorder menghasilkan: 8 * 5 + 9 / 7 - 4
      - Ini SALAH karena 7-4 harus dievaluasi sebelum /, tapi inorder
        tidak merefleksikan precedence → perlu tambah '(' dan ')' eksplisit.
      - _buildString() menambah '(' sebelum rekursi kiri dan ')' setelah kanan.

    Kedalaman maksimum stack rekursi _buildString() untuk pohon tinggi h:
      = h (satu frame per level, karena rekursi mengikuti path root ke leaf)

    b. HEAP ARRAY & SIFT-DOWN:
    -----------------------------------------------------------------------
    Rumus parent = (i-1)//2, left = 2*i+1, right = 2*i+2 valid hanya untuk
    COMPLETE BINARY TREE karena:
      - Complete tree mengisi level dari kiri ke kanan tanpa "lubang".
      - Pemetaan level-order ke array tanpa index terlewat.
      - Jika ada "lubang" (node hilang di tengah), formula menghasilkan
        indeks yang menunjuk ke elemen yang bukan anak sebenarnya.

    sift_down() setelah ekstraksi akar:
      1. Salin nilai dari leaf terakhir ke root.
      2. Bandingkan root dengan anak kiri dan kanan.
      3. Swap root dengan anak TERBESAR (jika anak lebih besar dari root).
      4. Ulangi di posisi baru sampai heap order property pulih atau leaf tercapai.

    Jumlah perbandingan maksimum dalam satu sift_down() untuk heap n elemen:
      - Tinggi heap = floor(log2(n)).
      - Per level: 2 perbandingan (root vs left, root vs right → pilih largest).
      - Total = 2 × floor(log2(n)) = O(log n) perbandingan.

    c. HEAPSORT IN-PLACE vs SIMPLE:
    -----------------------------------------------------------------------
    1. Kompleksitas ruang tambahan:
       - Simple (Listing 13.11): O(n) → alokasi MaxHeap array terpisah.
       - In-Place (Listing 13.12): O(1) → hanya variabel indeks/counter.

    2. Pola akses memori (cache locality):
       - Simple: akses melompat antara array input dan array heap → cache miss tinggi.
       - In-Place: semua operasi pada array yang sama → lebih cache-friendly,
         tapi swap tidak berurutan → masih ada cache miss, tapi lebih baik dari simple.

    3. Risiko overflow RAM terbatas:
       - Simple: alokasi O(n) bisa gagal jika RAM tidak cukup.
       - In-Place: hanya butuh beberapa variabel → aman di embedded system.

    In-place heapsort tetap O(n log n) karena:
      - Fase 1 (build heap): n/2 panggilan sift_down() × O(log n) = O(n log n).
        (Analisis lebih ketat: O(n) dengan argumen geometric series.)
      - Fase 2 (extract & sort): n panggilan sift_down() × O(log n) = O(n log n).
      - Swap array adalah O(1) → tidak menambah kompleksitas.

    d. HEAPSORT & BATAS TEORETIS:
    -----------------------------------------------------------------------
    Heapsort TIDAK melanggar batas Ω(n log n) karena:
      - Heapsort adalah comparison sort (menggunakan <, > untuk membandingkan elemen).
      - Batas Ω(n log n) berlaku untuk SEMUA comparison sort.
      - Heapsort memang O(n log n) = tepat di batas bawah.

    Property null link di Decision Tree Morse Code:
      - Saat decode sequence, kita traverse pohon mengikuti '.' (kiri) atau '-' (kanan).
      - Jika child = null → sequence tidak valid (tidak ada kode Morse dengan prefix itu).
      - Pengecekan: if node.left is None dan simbol = '.' → return None / error.

    Pendekatan rekursif lebih cocok untuk membangun pohon keputusan karena:
      - Struktur pohon itu sendiri rekursif (setiap subtree juga pohon).
      - Backtracking otomatis saat rekursi unwind → tidak perlu stack manual.
      - Kode lebih ringkas dan mudah dibaca.
      - Iteratif membutuhkan stack eksplisit + pointer navigasi → lebih kompleks.
    =========================================================================
    """

    def __init__(self, expr_str: str):
        self.expr = expr_str
        self.values = []

    # =========================================================================
    # EXPRESSION TREE: Builder & Evaluator
    # =========================================================================

    def parse_and_evaluate(self) -> List[int]:
        """
        Membangun pohon ekspresi dari string terparentheses penuh,
        lalu mengevaluasi dan mengembalikan list nilai integer.

        Contoh: "((8*5)+(9/(7-4)))" → evaluasi → [43]
        """
        # Bersihkan spasi
        clean = self.expr.replace(" ", "")
        tokens = deque(clean)
        root = self._build_tree(tokens)
        result = self._eval_tree(root)
        self.values = [result]
        return self.values

    def _build_tree(self, tokens: deque) -> Optional[dict]:
        """
        Implementasi rekursif sesuai Listing 13.9 menggunakan dict sebagai node.
        Node: {'val': operator_or_operand, 'left': node, 'right': node}

        Aturan parsing:
          - '(' → buat subtree: rekursi kiri, operator, rekursi kanan, skip ')'
          - digit/huruf → node leaf dengan nilai tersebut
        """
        if not tokens:
            return None

        token = tokens.popleft()

        if token == '(':
            # Bangun subtree kiri
            left_node = self._build_tree(tokens)

            # Token berikutnya = operator
            operator = tokens.popleft()

            # Bangun subtree kanan
            right_node = self._build_tree(tokens)

            # Konsumsi ')' penutup
            if tokens and tokens[0] == ')':
                tokens.popleft()

            return {'val': operator, 'left': left_node, 'right': right_node}

        else:
            # Token adalah operand (digit atau huruf variabel)
            return {'val': token, 'left': None, 'right': None}

    def _eval_tree(self, node: Optional[dict]) -> float:
        """
        Evaluasi pohon ekspresi secara POSTORDER (kiri → kanan → node).

        Postorder digunakan karena:
          - Kedua subtree harus dievaluasi SEBELUM operator bisa diproses.
          - Ini sesuai dengan urutan evaluasi ekspresi aritmetika.

        Menangani:
          - Digit tunggal (operand literal).
          - Operator: +, -, *, /, %
          - Division by zero → raise ValueError.
        """
        if node is None:
            return 0

        # Leaf node: operand
        if node['left'] is None and node['right'] is None:
            try:
                return float(node['val'])
            except ValueError:
                raise ValueError(f"Token tidak valid sebagai operand: '{node['val']}'")

        # Interior node: operator
        left_val = self._eval_tree(node['left'])
        right_val = self._eval_tree(node['right'])
        op = node['val']

        if op == '+':
            return left_val + right_val
        elif op == '-':
            return left_val - right_val
        elif op == '*':
            return left_val * right_val
        elif op == '/':
            if right_val == 0:
                raise ValueError("Pembagian dengan nol!")
            return left_val / right_val
        elif op == '%':
            if right_val == 0:
                raise ValueError("Modulo dengan nol!")
            return left_val % right_val
        else:
            raise ValueError(f"Operator tidak dikenal: '{op}'")

    def _tree_to_postfix(self, node: Optional[dict]) -> str:
        """
        Helper: traversal POSTORDER menghasilkan notasi POSTFIX.
        Tidak butuh tanda kurung karena urutan traversal sudah benar.
        """
        if node is None:
            return ""
        left = self._tree_to_postfix(node['left'])
        right = self._tree_to_postfix(node['right'])
        val = str(node['val'])
        result = ""
        if left:
            result += left + " "
        if right:
            result += right + " "
        result += val
        return result

    def _tree_to_infix(self, node: Optional[dict]) -> str:
        """
        Helper: traversal INORDER dengan tanda kurung eksplisit (seperti Listing 13.7).
        Tanpa kurung, hasil inorder bisa ambigu karena precedence hilang.
        """
        if node is None:
            return ""
        # Leaf
        if node['left'] is None and node['right'] is None:
            return str(node['val'])
        # Interior: tambah '(' dan ')' mengapit setiap subtree
        left_str = self._tree_to_infix(node['left'])
        right_str = self._tree_to_infix(node['right'])
        return f"({left_str}{node['val']}{right_str})"

    # =========================================================================
    # IN-PLACE HEAPSORT
    # =========================================================================

    def heapsort_inplace(self, arr: List[int]) -> List[int]:
        """
        Mengurutkan array secara ASCENDING menggunakan IN-PLACE heapsort.

        Fase 1 — Build Max-Heap:
          Mulai dari parent terakhir (n//2 - 1) ke root (0).
          Setiap node di-sift-down agar heap order property terpenuhi.
          Kompleksitas: O(n) — terbukti via geometric series (bukan O(n log n)).

        Fase 2 — Extract & Sort:
          Swap root (max) dengan elemen terakhir heap.
          Kurangi heap_size, sift-down root baru.
          Ulangi n-1 kali.
          Kompleksitas: O(n log n).

        Total: O(n log n), ruang ekstra O(1).
        """
        n = len(arr)
        if n <= 1:
            return arr

        # --- Fase 1: Build max-heap in-place ---
        # Mulai dari parent node terakhir (daun tidak perlu di-sift)
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(arr, n, i)

        # --- Fase 2: Extract max satu per satu ---
        for end in range(n - 1, 0, -1):
            # Swap root (max) ke posisi akhir subarray heap
            arr[0], arr[end] = arr[end], arr[0]
            # Pulihkan heap order untuk subarray yang mengecil
            self._sift_down(arr, end, 0)

        return arr

    def _sift_down(self, arr: List[int], heap_size: int, idx: int):
        """
        Sift-down dari indeks idx dalam heap berukuran heap_size.

        Mekanisme:
          1. Hitung indeks anak kiri (2*idx+1) dan kanan (2*idx+2).
          2. Temukan 'largest' di antara node saat ini, kiri, kanan.
          3. Jika largest != idx → swap, lanjut sift-down ke posisi baru.
          4. Loop sampai posisi stabil (largest == idx) atau leaf tercapai.

        Jumlah perbandingan maksimum = 2 × floor(log2(heap_size)) = O(log n).
        """
        while True:
            left = 2 * idx + 1   # indeks anak kiri
            right = 2 * idx + 2  # indeks anak kanan
            largest = idx        # asumsikan node saat ini terbesar

            # Bandingkan dengan anak kiri
            if left < heap_size and arr[left] > arr[largest]:
                largest = left

            # Bandingkan dengan anak kanan
            if right < heap_size and arr[right] > arr[largest]:
                largest = right

            # Jika anak lebih besar → swap dan lanjut
            if largest != idx:
                arr[idx], arr[largest] = arr[largest], arr[idx]
                idx = largest  # turun ke posisi anak
            else:
                break  # Heap order terpenuhi → berhenti

    # =========================================================================
    # COMPLETE BINARY TREE VALIDATOR
    # =========================================================================

    def is_complete_tree(self, arr: List[int]) -> bool:
        """
        Memvalidasi apakah array memenuhi properti COMPLETE BINARY TREE
        ketika dipetakan ke struktur heap (level-order).

        Properti complete binary tree pada array:
          - Semua indeks 0 sampai n-1 harus terisi TANPA lubang.
          - Untuk setiap node di indeks i:
            - Jika 2*i+1 < n → node kiri ADA (valid).
            - Jika 2*i+2 < n → node kanan ADA (valid).
            - Jika node kanan ada tapi node kiri tidak ada → TIDAK valid
              (melanggar properti "isi dari kiri ke kanan").

        Untuk array yang diisi berurutan 0..n-1, kondisi ini selalu terpenuhi
        selama tidak ada "lubang" di tengah.

        Kompleksitas: O(n).
        """
        n = len(arr)
        if n == 0:
            return True

        # Cek setiap node: jika ada anak kanan tapi tidak ada anak kiri → tidak complete
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2

            # Jika tidak ada anak kiri tapi ada anak kanan → tidak complete
            if left >= n and right < n:
                return False

            # Jika ada anak kiri tapi indeksnya melampaui array → tidak valid
            # (ini tidak mungkin terjadi untuk array kontinu, tapi dicek untuk keamanan)
            if right < n and left >= n:
                return False

        # Semua node memiliki anak yang valid → complete binary tree
        return True


# ============================================================================
# TESTING & DEMO
# ============================================================================

def linked_list_from_list(data: list) -> Optional[ListNode]:
    """Helper: buat linked list dari Python list."""
    if not data:
        return None
    head = ListNode(data[0])
    current = head
    for val in data[1:]:
        current.next = ListNode(val)
        current = current.next
    return head


def linked_list_to_list(head: Optional[ListNode]) -> list:
    """Helper: konversi linked list ke Python list."""
    result = []
    current = head
    while current:
        result.append(current.data)
        current = current.next
    return result


def run_tests():
    print("=" * 70)
    print("TESTING AdvancedSorter")
    print("=" * 70)

    sorter = AdvancedSorter()

    # --- Test 1: Array Merge Sort ---
    print("\n[1] Array Merge Sort (Stable, O(n log n), O(n) space)")
    test_cases = [
        [10, 23, 51, 18, 4, 31, 13, 5],
        [1],
        [],
        [5, 5, 5, 3, 1],          # Duplicate values → stability test
        [9, 8, 7, 6, 5, 4, 3, 2, 1],  # Reverse sorted
        [1, 2, 3, 4, 5, 6, 7, 8, 9],  # Already sorted
    ]
    for tc in test_cases:
        result = sorter.sort_array(tc[:])
        expected = sorted(tc)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Input: {tc[:8]}{'...' if len(tc)>8 else ''} → {result}")

    # --- Test 2: Linked List Merge Sort ---
    print("\n[2] Linked List Merge Sort (Stable, O(n log n), O(log n) space)")
    ll_tests = [
        [23, 51, 2, 18, 4, 31],
        [1],
        [3, 2, 1],
        [5, 5, 3, 3, 1, 1],
    ]
    for tc in ll_tests:
        head = linked_list_from_list(tc)
        sorted_head = sorter.sort_linked_list(head)
        result = linked_list_to_list(sorted_head)
        expected = sorted(tc)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Input: {tc} → {result}")

    # --- Test 3: Quick Sort ---
    print("\n[3] Quick Sort (Median-of-Three, fallback to merge sort)")
    qs_tests = [
        [10, 23, 51, 18, 4, 31, 13, 5],
        [5, 4, 3, 2, 1],           # Reverse sorted (worst case untuk pivot pertama)
        [1, 2, 3, 4, 5, 6, 7, 8],  # Already sorted
        [7, 7, 7, 7],              # All same
    ]
    for tc in qs_tests:
        result = sorter.quick_sort(tc[:])
        expected = sorted(tc)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Input: {tc} → {result}")

    print("\n" + "=" * 70)
    print("TESTING ExprHeapSorter")
    print("=" * 70)

    # --- Test 4: Expression Tree ---
    print("\n[4] Expression Tree Parser & Evaluator")
    expr_tests = [
        ("((8*5)+(9/(7-4)))", 40 + 3),   # = 43
        ("(5+8)", 13),
        ("((2*7)+8)", 22),
        ("(9+3)", 12),
    ]

    ehs = ExprHeapSorter("((8*5)+(9/(7-4)))")

    for expr, expected in expr_tests:
        ehs.expr = expr
        tokens = deque(expr.replace(" ", ""))
        root = ehs._build_tree(tokens)
        result = ehs._eval_tree(root)

        # Tampilkan notasi postfix dan infix
        tokens2 = deque(expr.replace(" ", ""))
        root2 = ehs._build_tree(tokens2)
        postfix = ehs._tree_to_postfix(root2)

        tokens3 = deque(expr.replace(" ", ""))
        root3 = ehs._build_tree(tokens3)
        infix = ehs._tree_to_infix(root3)

        status = "✓" if abs(result - expected) < 1e-9 else "✗"
        print(f"  {status} Expr: {expr}")
        print(f"       Infix (dengan kurung): {infix}")
        print(f"       Postfix (tanpa kurung): {postfix}")
        print(f"       Hasil: {result} (expected: {expected})")

    # --- Test 5: In-Place Heapsort ---
    print("\n[5] In-Place Heapsort (O(n log n), O(1) space)")
    heap_tests = [
        [64, 51, 31, 18, 29, 2, 13, 5, 10, 4, 23],
        [10, 51, 2, 18, 4, 31, 13, 5, 23, 64, 29],
        [5, 5, 5, 3, 1],
        [1],
        [],
    ]
    ehs2 = ExprHeapSorter("")
    for tc in heap_tests:
        result = ehs2.heapsort_inplace(tc[:])
        expected = sorted(tc)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Input: {tc[:8]}{'...' if len(tc)>8 else ''} → {result}")

    # --- Test 6: Complete Tree Validator ---
    print("\n[6] Complete Binary Tree Validator")
    ct_tests = [
        ([1, 2, 3, 4, 5, 6, 7], True),     # Perfect binary tree
        ([1, 2, 3, 4, 5, 6], True),          # Complete tree
        ([1, 2, 3], True),
        ([], True),
        ([1], True),
    ]
    ehs3 = ExprHeapSorter("")
    for arr, expected in ct_tests:
        result = ehs3.is_complete_tree(arr)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Array: {arr} → is_complete={result}")

    # --- Test 7: Full Pipeline Demo ---
    print("\n[7] DEMO PIPELINE LENGKAP (Parse → Heap → Sort)")
    print("  Ekspresi: ((8*5)+(9/(7-4)))")

    pipeline = ExprHeapSorter("((8*5)+(9/(7-4)))")
    values = pipeline.parse_and_evaluate()
    print(f"  Hasil evaluasi: {values[0]}")

    # Tambahkan 7 nilai acak untuk demo heap
    demo_arr = [int(values[0]), 12, 7, 34, 56, 3, 89, 21]
    print(f"  Array sebelum sort: {demo_arr}")
    sorted_arr = pipeline.heapsort_inplace(demo_arr[:])
    print(f"  Array setelah heapsort: {sorted_arr}")
    print(f"  Is complete tree? {pipeline.is_complete_tree(sorted_arr)}")

    print("\n" + "=" * 70)
    print("SEMUA TEST SELESAI")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()