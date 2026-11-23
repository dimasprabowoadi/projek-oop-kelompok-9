import tkinter as tk
from tkinter import ttk, messagebox

from models.bank_sampah import BankSampah
from models.jenis_sampah import JENIS_SAMPAH
from models.penyetor import Penyetor
from services.layanan_setoran import LayananSetoran
from utils.format import format_poin


class AplikasiBankSampah(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank Sampah Kampus")
        self.geometry("640x460")
        self.minsize(560, 420)

        self.bank = BankSampah("Bank Sampah Kampus")
        self.layanan = LayananSetoran(self.bank)
        self.entry_berat = {}

        self.buat_tampilan()
        self.refresh()

    def buat_tampilan(self):
        judul = ttk.Label(self, text="♻️ Bank Sampah Kampus", font=("Segoe UI", 16, "bold"))
        judul.pack(pady=(10, 5))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        tab_daftar = ttk.Frame(notebook, padding=15)
        tab_setor = ttk.Frame(notebook, padding=15)
        tab_penyetor = ttk.Frame(notebook, padding=10)
        tab_riwayat = ttk.Frame(notebook, padding=10)
        notebook.add(tab_daftar, text="Daftar Penyetor")
        notebook.add(tab_setor, text="Catat Setoran")
        notebook.add(tab_penyetor, text="Penyetor & Poin")
        notebook.add(tab_riwayat, text="Riwayat")

        self.buat_tab_daftar(tab_daftar)
        self.buat_tab_setor(tab_setor)
        self.buat_tab_penyetor(tab_penyetor)
        self.buat_tab_riwayat(tab_riwayat)

        self.status = ttk.Label(self, anchor="center")
        self.status.pack(fill="x", pady=5)

    def buat_tab_daftar(self, tab):
        ttk.Label(tab, text="NIM").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nim = ttk.Entry(tab, width=30)
        self.entry_nim.grid(row=0, column=1, pady=5, padx=10)

        ttk.Label(tab, text="Nama").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_nama = ttk.Entry(tab, width=30)
        self.entry_nama.grid(row=1, column=1, pady=5, padx=10)

        ttk.Button(tab, text="Daftarkan", command=self.daftar_penyetor).grid(
            row=2, column=1, sticky="w", padx=10, pady=10
        )

    def buat_tab_setor(self, tab):
        ttk.Label(tab, text="Penyetor").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_penyetor = ttk.Combobox(tab, state="readonly", width=28)
        self.combo_penyetor.grid(row=0, column=1, pady=5, padx=10)

        for i, (jenis, kelas) in enumerate(JENIS_SAMPAH.items(), start=1):
            ttk.Label(tab, text=f"Berat {jenis} (kg) - {kelas.POIN_PER_KG} poin/kg").grid(
                row=i, column=0, sticky="w", pady=5
            )
            entry = ttk.Entry(tab, width=30)
            entry.insert(0, "0")
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.entry_berat[jenis] = entry

        ttk.Button(tab, text="Simpan Setoran", command=self.simpan_setoran).grid(
            row=len(JENIS_SAMPAH) + 1, column=1, sticky="w", padx=10, pady=10
        )

    def buat_tab_penyetor(self, tab):
        self.tabel_penyetor = ttk.Treeview(
            tab, columns=("nim", "nama", "poin"), show="headings"
        )
        for kolom, teks, lebar in (("nim", "NIM", 120), ("nama", "Nama", 220), ("poin", "Total Poin", 120)):
            self.tabel_penyetor.heading(kolom, text=teks)
            self.tabel_penyetor.column(kolom, width=lebar)
        self.tabel_penyetor.pack(fill="both", expand=True)

    def buat_tab_riwayat(self, tab):
        self.tabel_riwayat = ttk.Treeview(
            tab, columns=("no", "penyetor", "isi", "poin"), show="headings"
        )
        for kolom, teks, lebar in (("no", "No", 40), ("penyetor", "Penyetor", 110),
                                   ("isi", "Isi Setoran", 270), ("poin", "Poin", 90)):
            self.tabel_riwayat.heading(kolom, text=teks)
            self.tabel_riwayat.column(kolom, width=lebar)
        self.tabel_riwayat.pack(fill="both", expand=True)

    def daftar_penyetor(self):
        nim = self.entry_nim.get().strip()
        nama = self.entry_nama.get().strip()
        if not nim or not nama:
            messagebox.showerror("Error", "NIM dan nama harus diisi.")
            return
        try:
            self.bank.tambah_penyetor(Penyetor(nim, nama))
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        messagebox.showinfo("Berhasil", f"{nama} berhasil didaftarkan.")
        self.entry_nim.delete(0, tk.END)
        self.entry_nama.delete(0, tk.END)
        self.refresh()

    def simpan_setoran(self):
        indeks = self.combo_penyetor.current()
        if indeks < 0:
            messagebox.showerror("Error", "Pilih penyetor dulu.")
            return
        penyetor = self.bank.daftar_penyetor[indeks]

        daftar_sampah = []
        try:
            for jenis, entry in self.entry_berat.items():
                teks = entry.get().strip().replace(",", ".") or "0"
                berat = float(teks)
                if berat < 0:
                    raise ValueError("Berat tidak boleh negatif.")
                if berat > 0:
                    daftar_sampah.append(JENIS_SAMPAH[jenis](berat))
        except ValueError:
            messagebox.showerror("Error", "Berat harus berupa angka positif, contoh: 2 atau 1.5")
            return

        try:
            setoran = self.layanan.catat_setoran(penyetor.nim, daftar_sampah)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo(
            "Berhasil",
            f"Setoran #{setoran.nomor} tersimpan: {format_poin(setoran.total_poin())}",
        )
        for entry in self.entry_berat.values():
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        self.refresh()

    def refresh(self):
        penyetor = self.bank.daftar_penyetor
        self.combo_penyetor["values"] = [f"{p.nim} - {p.nama}" for p in penyetor]

        self.tabel_penyetor.delete(*self.tabel_penyetor.get_children())
        for p in penyetor:
            self.tabel_penyetor.insert("", tk.END, values=(p.nim, p.nama, format_poin(p.total_poin)))

        self.tabel_riwayat.delete(*self.tabel_riwayat.get_children())
        for s in reversed(self.bank.daftar_setoran):
            isi = ", ".join(f"{i.sampah.jenis} {i.sampah.berat} kg" for i in s.items)
            self.tabel_riwayat.insert(
                "", tk.END, values=(s.nomor, s.penyetor.nama, isi, format_poin(s.total_poin()))
            )

        total = sum(p.total_poin for p in penyetor)
        self.status.config(
            text=f"Penyetor: {len(penyetor)}  |  Setoran: {len(self.bank.daftar_setoran)}  |  Total: {format_poin(total)}"
        )


if __name__ == "__main__":
    AplikasiBankSampah().mainloop()