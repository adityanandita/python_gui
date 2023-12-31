# Buat dictionary yang berisi data dummy untuk profile PCR 1-6
import random
profile_PCR = {
    1: {
        'nama_profile': 'WSSV',
        'suhu_inisialisasi': 95,
        'suhu_denaturasi': 94,
        'suhu_annealing': 55,
        'suhu_ekstensi': 72,
        'suhu_finalisasi': 72,
        'waktu_inisialisasi': 0,
        'waktu_denaturasi': 0,
        'waktu_annealing': 0,
        'waktu_ekstensi': 0,
        'waktu_finalisasi': 1,
        'suhu': [95, 94, 55, 72, 72],
        'waktu': [5, 5, 5, 5, 5],
        'jumlah_cycle': 9
    },
    2: {
        'nama_profile': 'IMNV',
        'suhu_inisialisasi': 94,
        'suhu_denaturasi': 93,
        'suhu_annealing': 54,
        'suhu_ekstensi': 71,
        'suhu_finalisasi': 71,
        'waktu_inisialisasi': 4,
        'waktu_denaturasi': 29,
        'waktu_annealing': 29,
        'waktu_ekstensi': 59,
        'waktu_finalisasi': 9,
        'suhu': [94, 93, 54, 71, 71],
        'waktu': [4, 29, 29, 59, 9],
        'jumlah_cycle': 34
    },
    3: {
        'nama_profile': 'TSV',
        'suhu_inisialisasi': 93,
        'suhu_denaturasi': 92,
        'suhu_annealing': 53,
        'suhu_ekstensi': 70,
        'suhu_finalisasi': 70,
        'waktu_inisialisasi': 3,
        'waktu_denaturasi': 28,
        'waktu_annealing': 28,
        'waktu_ekstensi': 58,
        'waktu_finalisasi': 8,
        'suhu': [93, 92, 53, 70, 70],
        'waktu': [3, 28, 28, 58, 8],
        'jumlah_cycle': 33
    },
    4: {
        'nama_profile': 'MBV',
        'suhu_inisialisasi': 93,
        'suhu_denaturasi': 92,
        'suhu_annealing': 53,
        'suhu_ekstensi': 70,
        'suhu_finalisasi': 70,
        'waktu_inisialisasi': 3,
        'waktu_denaturasi': 28,
        'waktu_annealing': 28,
        'waktu_ekstensi': 58,
        'waktu_finalisasi': 8,
        'suhu': [93, 92, 53, 70, 70],
        'waktu': [3, 28, 28, 58, 8],
        'jumlah_cycle': 33
    },
}
