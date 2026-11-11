/* Not part of zlib: this project's file, passed with --preinclude to every unit of
   the zlib 1.2.5 copy. The image links two zlib copies (notes/COMPILER.md), so this
   copy's functions keep their analysis names (fn_<address>) from config/jpn/symbols.txt
   and the source is compiled under those names. Each address was found by compiling
   the unaltered 1.2.5 source and matching the function in the image. */
#ifndef ZLIB125_NAMES_H
#define ZLIB125_NAMES_H

#define _tr_align         fn_006A0B2C
#define _tr_flush_block   fn_006A0E2C
#define _tr_init          fn_006A153C
#define _tr_stored_block  fn_006A168C
#define adler32           fn_006A1860
#define build_tree        fn_006951B4
#define compress_block    fn_00695E8C
#define crc32             fn_006A1C10
#define crc32_big         fn_006968A0
#define deflate           fn_006A20E8
#define deflateEnd        fn_006A3168
#define deflateInit2_     fn_006A3248
#define deflateReset      fn_006A34D4
#define deflate_fast      fn_006974D4
#define deflate_slow      fn_00698264
#define deflate_stored    fn_00698B94
#define fill_window       fn_0069912C
#define flush_pending     fn_006994F0
#define inflate           fn_006A360C
#define inflateEnd        fn_006A4FB0
#define inflateInit2_     fn_006A500C
#define inflateInit_      fn_006A4FFC
#define inflateReset      fn_006A5150
#define inflate_fast      fn_006A51E4
#define inflate_table     fn_006A594C
#define scan_tree         fn_006A6088
#define send_tree         fn_006A6718
#define updatewindow      fn_006B0CA8
#define zcalloc           fn_006A5F60
#define zcfree            fn_006A5F68

/* Data the functions above refer to, at this copy's addresses. */
#define _dist_code          lbl_0076A2EC
#define _length_code        lbl_0076A4EC
#define configuration_table lbl_00748968
#define lenfix              lbl_007489E0
#define order               lbl_00749260
#define z_errmsg            lbl_0076A724

#endif
