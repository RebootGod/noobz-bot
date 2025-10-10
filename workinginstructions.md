# Rule and Instruction need to follow

- Gue lebih suka structure file yang professional
- Gue lebih suka kalo setiap function, logic, fitur, punya file tersendiri
- Gue lebih suka kalo setiap fitur, function, punya file nya tersendiri. Agar lebih mudah pada saat debug atau fixing
- Gue lebih suka kalo setiap fitur, function, punya file nya tersendiri, karena bisa dipakai untuk page lain kalo dibutuhkan. Jadi gaperlu bikin function baru, logic baru, fitur baru, atau apapun yang baru
- Gue lebih suka kalo setiap file memiliki maksimal 300 baris, kalo gak cukup bikin file lain. Kenapa bikin file lain? Kita memakai konsep reusability soalnya
    Contoh, file untuk login sudah maksmimal 300 baris, buat file login_2 untuk lanjutin, dan ubah nama file login menjadi login_1

- Selalu lakukan deep checking dan validation untuk memastikan tidak ada yang terlewat, tertinggal, atau malah jadi error

# You need to write "Aku sudah membaca workinginstruction.md dan mengerti (jelaskan apa yang lo ngerti)"