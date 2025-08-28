```mermaid
flowchart TD
    root["summary IDS"]

    n1(summary)
    root --> n1
    class n1 complexNode
    n2[type]
    n1 --> n2
    class n2 normalNode
    n3[name]
    n2 --> n3
    class n3 leafNode
    n4[index]
    n2 --> n4
    class n4 leafNode
    n5[description]
    n2 --> n5
    class n5 leafNode
    n6[machine]
    n1 --> n6
    class n6 leafNode
    n7[pulse]
    n1 --> n7
    class n7 leafNode
    n8[pulse_time_begin]
    n1 --> n8
    class n8 leafNode
    n9[pulse_time_begin_epoch]
    n1 --> n9
    class n9 normalNode
    n10[seconds]
    n9 --> n10
    class n10 leafNode
    n11[nanoseconds]
    n9 --> n11
    class n11 leafNode
    n12[pulse_time_end_epoch]
    n1 --> n12
    class n12 normalNode
    n13[seconds]
    n12 --> n13
    class n13 leafNode
    n14[nanoseconds]
    n12 --> n14
    class n14 leafNode
    n15[pulse_processing_time_begin]
    n1 --> n15
    class n15 leafNode
    n16[description_before]
    n1 --> n16
    class n16 leafNode
    n17[description_after]
    n1 --> n17
    class n17 leafNode
    n18[simulation]
    n1 --> n18
    class n18 normalNode
    n19[time_begin]
    n18 --> n19
    class n19 leafNode
    n20[time_step]
    n18 --> n20
    class n20 leafNode
    n21[time_end]
    n18 --> n21
    class n21 leafNode
    n22[workflow]
    n18 --> n22
    class n22 leafNode
    n23[tag]
    n1 --> n23
    class n23 normalNode
    n24[name]
    n23 --> n24
    class n24 leafNode
    n25[comment]
    n23 --> n25
    class n25 leafNode
    n26[configuration]
    n1 --> n26
    class n26 normalNode
    n27[value]
    n26 --> n27
    class n27 leafNode
    n28[source]
    n26 --> n28
    class n28 leafNode
    n29[magnetic_shear_flag]
    n1 --> n29
    class n29 normalNode
    n30[value]
    n29 --> n30
    class n30 leafNode
    n31[source]
    n29 --> n31
    class n31 leafNode
    n32[stationary_phase_flag]
    n1 --> n32
    class n32 normalNode
    n33[value]
    n32 --> n33
    class n33 leafNode
    n34[source]
    n32 --> n34
    class n34 leafNode
    n35[midplane]
    n1 --> n35
    class n35 normalNode
    n36[name]
    n35 --> n36
    class n36 leafNode
    n37[index]
    n35 --> n37
    class n37 leafNode
    n38[description]
    n35 --> n38
    class n38 leafNode
    n39(composition)
    n1 --> n39
    class n39 complexNode
    n40[hydrogen]
    n39 --> n40
    class n40 normalNode
    n41[value]
    n40 --> n41
    class n41 leafNode
    n42[source]
    n40 --> n42
    class n42 leafNode
    n43[deuterium]
    n39 --> n43
    class n43 normalNode
    n44[value]
    n43 --> n44
    class n44 leafNode
    n45[source]
    n43 --> n45
    class n45 leafNode
    n46[tritium]
    n39 --> n46
    class n46 normalNode
    n47[value]
    n46 --> n47
    class n47 leafNode
    n48[source]
    n46 --> n48
    class n48 leafNode
    n49[deuterium_tritium]
    n39 --> n49
    class n49 normalNode
    n50[value]
    n49 --> n50
    class n50 leafNode
    n51[source]
    n49 --> n51
    class n51 leafNode
    n52[helium_3]
    n39 --> n52
    class n52 normalNode
    n53[value]
    n52 --> n53
    class n53 leafNode
    n54[source]
    n52 --> n54
    class n54 leafNode
    n55[helium_4]
    n39 --> n55
    class n55 normalNode
    n56[value]
    n55 --> n56
    class n56 leafNode
    n57[source]
    n55 --> n57
    class n57 leafNode
    n58[beryllium]
    n39 --> n58
    class n58 normalNode
    n59[value]
    n58 --> n59
    class n59 leafNode
    n60[source]
    n58 --> n60
    class n60 leafNode
    n61[boron]
    n39 --> n61
    class n61 normalNode
    n62[value]
    n61 --> n62
    class n62 leafNode
    n63[source]
    n61 --> n63
    class n63 leafNode
    n64[lithium]
    n39 --> n64
    class n64 normalNode
    n65[value]
    n64 --> n65
    class n65 leafNode
    n66[source]
    n64 --> n66
    class n66 leafNode
    n67[carbon]
    n39 --> n67
    class n67 normalNode
    n68[value]
    n67 --> n68
    class n68 leafNode
    n69[source]
    n67 --> n69
    class n69 leafNode
    n70[nitrogen]
    n39 --> n70
    class n70 normalNode
    n71[value]
    n70 --> n71
    class n71 leafNode
    n72[source]
    n70 --> n72
    class n72 leafNode
    n73[neon]
    n39 --> n73
    class n73 normalNode
    n74[value]
    n73 --> n74
    class n74 leafNode
    n75[source]
    n73 --> n75
    class n75 leafNode
    n76[argon]
    n39 --> n76
    class n76 normalNode
    n77[value]
    n76 --> n77
    class n77 leafNode
    n78[source]
    n76 --> n78
    class n78 leafNode
    n79[xenon]
    n39 --> n79
    class n79 normalNode
    n80[value]
    n79 --> n80
    class n80 leafNode
    n81[source]
    n79 --> n81
    class n81 leafNode
    n82[oxygen]
    n39 --> n82
    class n82 normalNode
    n83[value]
    n82 --> n83
    class n83 leafNode
    n84[source]
    n82 --> n84
    class n84 leafNode
    n85[tungsten]
    n39 --> n85
    class n85 normalNode
    n86[value]
    n85 --> n86
    class n86 leafNode
    n87[source]
    n85 --> n87
    class n87 leafNode
    n88[iron]
    n39 --> n88
    class n88 normalNode
    n89[value]
    n88 --> n89
    class n89 leafNode
    n90[source]
    n88 --> n90
    class n90 leafNode
    n91[krypton]
    n39 --> n91
    class n91 normalNode
    n92[value]
    n91 --> n92
    class n92 leafNode
    n93[source]
    n91 --> n93
    class n93 leafNode
    n94(global_quantities)
    n1 --> n94
    class n94 complexNode
    n95[ip]
    n94 --> n95
    class n95 normalNode
    n96[value]
    n95 --> n96
    class n96 leafNode
    n97[source]
    n95 --> n97
    class n97 leafNode
    n98[current_non_inductive]
    n94 --> n98
    class n98 normalNode
    n99[value]
    n98 --> n99
    class n99 leafNode
    n100[source]
    n98 --> n100
    class n100 leafNode
    n101[current_bootstrap]
    n94 --> n101
    class n101 normalNode
    n102[value]
    n101 --> n102
    class n102 leafNode
    n103[source]
    n101 --> n103
    class n103 leafNode
    n104[current_ohm]
    n94 --> n104
    class n104 normalNode
    n105[value]
    n104 --> n105
    class n105 leafNode
    n106[source]
    n104 --> n106
    class n106 leafNode
    n107[current_alignment]
    n94 --> n107
    class n107 normalNode
    n108[value]
    n107 --> n108
    class n108 leafNode
    n109[source]
    n107 --> n109
    class n109 leafNode
    n110[v_loop]
    n94 --> n110
    class n110 normalNode
    n111[value]
    n110 --> n111
    class n111 leafNode
    n112[source]
    n110 --> n112
    class n112 leafNode
    n113[li_3]
    n94 --> n113
    class n113 normalNode
    n114[value]
    n113 --> n114
    class n114 leafNode
    n115[source]
    n113 --> n115
    class n115 leafNode
    n116[li_3_mhd]
    n94 --> n116
    class n116 normalNode
    n117[value]
    n116 --> n117
    class n117 leafNode
    n118[source]
    n116 --> n118
    class n118 leafNode
    n119[beta_tor]
    n94 --> n119
    class n119 normalNode
    n120[value]
    n119 --> n120
    class n120 leafNode
    n121[source]
    n119 --> n121
    class n121 leafNode
    n122[beta_tor_mhd]
    n94 --> n122
    class n122 normalNode
    n123[value]
    n122 --> n123
    class n123 leafNode
    n124[source]
    n122 --> n124
    class n124 leafNode
    n125[beta_tor_norm]
    n94 --> n125
    class n125 normalNode
    n126[value]
    n125 --> n126
    class n126 leafNode
    n127[source]
    n125 --> n127
    class n127 leafNode
    n128[beta_tor_norm_mhd]
    n94 --> n128
    class n128 normalNode
    n129[value]
    n128 --> n129
    class n129 leafNode
    n130[source]
    n128 --> n130
    class n130 leafNode
    n131[beta_tor_thermal_norm]
    n94 --> n131
    class n131 normalNode
    n132[value]
    n131 --> n132
    class n132 leafNode
    n133[source]
    n131 --> n133
    class n133 leafNode
    n134[beta_pol]
    n94 --> n134
    class n134 normalNode
    n135[value]
    n134 --> n135
    class n135 leafNode
    n136[source]
    n134 --> n136
    class n136 leafNode
    n137[beta_pol_mhd]
    n94 --> n137
    class n137 normalNode
    n138[value]
    n137 --> n138
    class n138 leafNode
    n139[source]
    n137 --> n139
    class n139 leafNode
    n140[energy_diamagnetic]
    n94 --> n140
    class n140 normalNode
    n141[value]
    n140 --> n141
    class n141 leafNode
    n142[source]
    n140 --> n142
    class n142 leafNode
    n143[denergy_diamagnetic_dt]
    n94 --> n143
    class n143 normalNode
    n144[value]
    n143 --> n144
    class n144 leafNode
    n145[source]
    n143 --> n145
    class n145 leafNode
    n146[energy_total]
    n94 --> n146
    class n146 normalNode
    n147[value]
    n146 --> n147
    class n147 leafNode
    n148[source]
    n146 --> n148
    class n148 leafNode
    n149[energy_mhd]
    n94 --> n149
    class n149 normalNode
    n150[value]
    n149 --> n150
    class n150 leafNode
    n151[source]
    n149 --> n151
    class n151 leafNode
    n152[energy_thermal]
    n94 --> n152
    class n152 normalNode
    n153[value]
    n152 --> n153
    class n153 leafNode
    n154[source]
    n152 --> n154
    class n154 leafNode
    n155[energy_ion_total_thermal]
    n94 --> n155
    class n155 normalNode
    n156[value]
    n155 --> n156
    class n156 leafNode
    n157[source]
    n155 --> n157
    class n157 leafNode
    n158[energy_electrons_thermal]
    n94 --> n158
    class n158 normalNode
    n159[value]
    n158 --> n159
    class n159 leafNode
    n160[source]
    n158 --> n160
    class n160 leafNode
    n161[denergy_thermal_dt]
    n94 --> n161
    class n161 normalNode
    n162[value]
    n161 --> n162
    class n162 leafNode
    n163[source]
    n161 --> n163
    class n163 leafNode
    n164[energy_b_field_pol]
    n94 --> n164
    class n164 normalNode
    n165[value]
    n164 --> n165
    class n165 leafNode
    n166[source]
    n164 --> n166
    class n166 leafNode
    n167[energy_fast_perpendicular]
    n94 --> n167
    class n167 normalNode
    n168[value]
    n167 --> n168
    class n168 leafNode
    n169[source]
    n167 --> n169
    class n169 leafNode
    n170[energy_fast_parallel]
    n94 --> n170
    class n170 normalNode
    n171[value]
    n170 --> n171
    class n171 leafNode
    n172[source]
    n170 --> n172
    class n172 leafNode
    n173[volume]
    n94 --> n173
    class n173 normalNode
    n174[value]
    n173 --> n174
    class n174 leafNode
    n175[source]
    n173 --> n175
    class n175 leafNode
    n176[h_mode]
    n94 --> n176
    class n176 normalNode
    n177[value]
    n176 --> n177
    class n177 leafNode
    n178[source]
    n176 --> n178
    class n178 leafNode
    n179[r0]
    n94 --> n179
    class n179 normalNode
    n180[value]
    n179 --> n180
    class n180 leafNode
    n181[source]
    n179 --> n181
    class n181 leafNode
    n182[b0]
    n94 --> n182
    class n182 normalNode
    n183[value]
    n182 --> n183
    class n183 leafNode
    n184[source]
    n182 --> n184
    class n184 leafNode
    n185[fusion_gain]
    n94 --> n185
    class n185 normalNode
    n186[value]
    n185 --> n186
    class n186 leafNode
    n187[source]
    n185 --> n187
    class n187 leafNode
    n188[h_98]
    n94 --> n188
    class n188 normalNode
    n189[value]
    n188 --> n189
    class n189 leafNode
    n190[source]
    n188 --> n190
    class n190 leafNode
    n191[tau_energy]
    n94 --> n191
    class n191 normalNode
    n192[value]
    n191 --> n192
    class n192 leafNode
    n193[source]
    n191 --> n193
    class n193 leafNode
    n194[tau_helium]
    n94 --> n194
    class n194 normalNode
    n195[value]
    n194 --> n195
    class n195 leafNode
    n196[source]
    n194 --> n196
    class n196 leafNode
    n197[tau_resistive]
    n94 --> n197
    class n197 normalNode
    n198[value]
    n197 --> n198
    class n198 leafNode
    n199[source]
    n197 --> n199
    class n199 leafNode
    n200[tau_energy_98]
    n94 --> n200
    class n200 normalNode
    n201[value]
    n200 --> n201
    class n201 leafNode
    n202[source]
    n200 --> n202
    class n202 leafNode
    n203[ratio_tau_helium_fuel]
    n94 --> n203
    class n203 normalNode
    n204[value]
    n203 --> n204
    class n204 leafNode
    n205[source]
    n203 --> n205
    class n205 leafNode
    n206[resistance]
    n94 --> n206
    class n206 normalNode
    n207[value]
    n206 --> n207
    class n207 leafNode
    n208[source]
    n206 --> n208
    class n208 leafNode
    n209[q_95]
    n94 --> n209
    class n209 normalNode
    n210[value]
    n209 --> n210
    class n210 leafNode
    n211[source]
    n209 --> n211
    class n211 leafNode
    n212[power_ohm]
    n94 --> n212
    class n212 normalNode
    n213[value]
    n212 --> n213
    class n213 leafNode
    n214[source]
    n212 --> n214
    class n214 leafNode
    n215[power_steady]
    n94 --> n215
    class n215 normalNode
    n216[value]
    n215 --> n216
    class n216 leafNode
    n217[source]
    n215 --> n217
    class n217 leafNode
    n218[power_radiated]
    n94 --> n218
    class n218 normalNode
    n219[value]
    n218 --> n219
    class n219 leafNode
    n220[source]
    n218 --> n220
    class n220 leafNode
    n221[power_radiated_inside_lcfs]
    n94 --> n221
    class n221 normalNode
    n222[value]
    n221 --> n222
    class n222 leafNode
    n223[source]
    n221 --> n223
    class n223 leafNode
    n224[power_radiated_outside_lcfs]
    n94 --> n224
    class n224 normalNode
    n225[value]
    n224 --> n225
    class n225 leafNode
    n226[source]
    n224 --> n226
    class n226 leafNode
    n227[power_line]
    n94 --> n227
    class n227 normalNode
    n228[value]
    n227 --> n228
    class n228 leafNode
    n229[source]
    n227 --> n229
    class n229 leafNode
    n230[power_bremsstrahlung]
    n94 --> n230
    class n230 normalNode
    n231[value]
    n230 --> n231
    class n231 leafNode
    n232[source]
    n230 --> n232
    class n232 leafNode
    n233[power_synchrotron]
    n94 --> n233
    class n233 normalNode
    n234[value]
    n233 --> n234
    class n234 leafNode
    n235[source]
    n233 --> n235
    class n235 leafNode
    n236[power_loss]
    n94 --> n236
    class n236 normalNode
    n237[value]
    n236 --> n237
    class n237 leafNode
    n238[source]
    n236 --> n238
    class n238 leafNode
    n239[greenwald_fraction]
    n94 --> n239
    class n239 normalNode
    n240[value]
    n239 --> n240
    class n240 leafNode
    n241[source]
    n239 --> n241
    class n241 leafNode
    n242[fusion_fluence]
    n94 --> n242
    class n242 normalNode
    n243[value]
    n242 --> n243
    class n243 leafNode
    n244[source]
    n242 --> n244
    class n244 leafNode
    n245[psi_external_average]
    n94 --> n245
    class n245 normalNode
    n246[value]
    n245 --> n246
    class n246 leafNode
    n247[source]
    n245 --> n247
    class n247 leafNode
    n248(local)
    n1 --> n248
    class n248 complexNode
    n249(magnetic_axis)
    n248 --> n249
    class n249 complexNode
    n250[position]
    n249 --> n250
    class n250 normalNode
    n251[rho_tor_norm]
    n250 --> n251
    class n251 leafNode
    n252[rho_tor]
    n250 --> n252
    class n252 leafNode
    n253[psi]
    n250 --> n253
    class n253 leafNode
    n254[r]
    n250 --> n254
    class n254 leafNode
    n255[z]
    n250 --> n255
    class n255 leafNode
    n256[t_e]
    n249 --> n256
    class n256 normalNode
    n257[value]
    n256 --> n257
    class n257 leafNode
    n258[source]
    n256 --> n258
    class n258 leafNode
    n259[t_i_average]
    n249 --> n259
    class n259 normalNode
    n260[value]
    n259 --> n260
    class n260 leafNode
    n261[source]
    n259 --> n261
    class n261 leafNode
    n262[n_e]
    n249 --> n262
    class n262 normalNode
    n263[value]
    n262 --> n263
    class n263 leafNode
    n264[source]
    n262 --> n264
    class n264 leafNode
    n265(n_i)
    n249 --> n265
    class n265 complexNode
    n266[hydrogen]
    n265 --> n266
    class n266 normalNode
    n267[value]
    n266 --> n267
    class n267 leafNode
    n268[source]
    n266 --> n268
    class n268 leafNode
    n269[deuterium]
    n265 --> n269
    class n269 normalNode
    n270[value]
    n269 --> n270
    class n270 leafNode
    n271[source]
    n269 --> n271
    class n271 leafNode
    n272[tritium]
    n265 --> n272
    class n272 normalNode
    n273[value]
    n272 --> n273
    class n273 leafNode
    n274[source]
    n272 --> n274
    class n274 leafNode
    n275[deuterium_tritium]
    n265 --> n275
    class n275 normalNode
    n276[value]
    n275 --> n276
    class n276 leafNode
    n277[source]
    n275 --> n277
    class n277 leafNode
    n278[helium_3]
    n265 --> n278
    class n278 normalNode
    n279[value]
    n278 --> n279
    class n279 leafNode
    n280[source]
    n278 --> n280
    class n280 leafNode
    n281[helium_4]
    n265 --> n281
    class n281 normalNode
    n282[value]
    n281 --> n282
    class n282 leafNode
    n283[source]
    n281 --> n283
    class n283 leafNode
    n284[beryllium]
    n265 --> n284
    class n284 normalNode
    n285[value]
    n284 --> n285
    class n285 leafNode
    n286[source]
    n284 --> n286
    class n286 leafNode
    n287[boron]
    n265 --> n287
    class n287 normalNode
    n288[value]
    n287 --> n288
    class n288 leafNode
    n289[source]
    n287 --> n289
    class n289 leafNode
    n290[lithium]
    n265 --> n290
    class n290 normalNode
    n291[value]
    n290 --> n291
    class n291 leafNode
    n292[source]
    n290 --> n292
    class n292 leafNode
    n293[carbon]
    n265 --> n293
    class n293 normalNode
    n294[value]
    n293 --> n294
    class n294 leafNode
    n295[source]
    n293 --> n295
    class n295 leafNode
    n296[nitrogen]
    n265 --> n296
    class n296 normalNode
    n297[value]
    n296 --> n297
    class n297 leafNode
    n298[source]
    n296 --> n298
    class n298 leafNode
    n299[neon]
    n265 --> n299
    class n299 normalNode
    n300[value]
    n299 --> n300
    class n300 leafNode
    n301[source]
    n299 --> n301
    class n301 leafNode
    n302[argon]
    n265 --> n302
    class n302 normalNode
    n303[value]
    n302 --> n303
    class n303 leafNode
    n304[source]
    n302 --> n304
    class n304 leafNode
    n305[xenon]
    n265 --> n305
    class n305 normalNode
    n306[value]
    n305 --> n306
    class n306 leafNode
    n307[source]
    n305 --> n307
    class n307 leafNode
    n308[oxygen]
    n265 --> n308
    class n308 normalNode
    n309[value]
    n308 --> n309
    class n309 leafNode
    n310[source]
    n308 --> n310
    class n310 leafNode
    n311[tungsten]
    n265 --> n311
    class n311 normalNode
    n312[value]
    n311 --> n312
    class n312 leafNode
    n313[source]
    n311 --> n313
    class n313 leafNode
    n314[iron]
    n265 --> n314
    class n314 normalNode
    n315[value]
    n314 --> n315
    class n315 leafNode
    n316[source]
    n314 --> n316
    class n316 leafNode
    n317[krypton]
    n265 --> n317
    class n317 normalNode
    n318[value]
    n317 --> n318
    class n318 leafNode
    n319[source]
    n317 --> n319
    class n319 leafNode
    n320[n_i_total]
    n249 --> n320
    class n320 normalNode
    n321[value]
    n320 --> n321
    class n321 leafNode
    n322[source]
    n320 --> n322
    class n322 leafNode
    n323[zeff]
    n249 --> n323
    class n323 normalNode
    n324[value]
    n323 --> n324
    class n324 leafNode
    n325[source]
    n323 --> n325
    class n325 leafNode
    n326[momentum_phi]
    n249 --> n326
    class n326 normalNode
    n327[value]
    n326 --> n327
    class n327 leafNode
    n328[source]
    n326 --> n328
    class n328 leafNode
    n329(velocity_phi)
    n249 --> n329
    class n329 complexNode
    n330[hydrogen]
    n329 --> n330
    class n330 normalNode
    n331[value]
    n330 --> n331
    class n331 leafNode
    n332[source]
    n330 --> n332
    class n332 leafNode
    n333[deuterium]
    n329 --> n333
    class n333 normalNode
    n334[value]
    n333 --> n334
    class n334 leafNode
    n335[source]
    n333 --> n335
    class n335 leafNode
    n336[tritium]
    n329 --> n336
    class n336 normalNode
    n337[value]
    n336 --> n337
    class n337 leafNode
    n338[source]
    n336 --> n338
    class n338 leafNode
    n339[deuterium_tritium]
    n329 --> n339
    class n339 normalNode
    n340[value]
    n339 --> n340
    class n340 leafNode
    n341[source]
    n339 --> n341
    class n341 leafNode
    n342[helium_3]
    n329 --> n342
    class n342 normalNode
    n343[value]
    n342 --> n343
    class n343 leafNode
    n344[source]
    n342 --> n344
    class n344 leafNode
    n345[helium_4]
    n329 --> n345
    class n345 normalNode
    n346[value]
    n345 --> n346
    class n346 leafNode
    n347[source]
    n345 --> n347
    class n347 leafNode
    n348[beryllium]
    n329 --> n348
    class n348 normalNode
    n349[value]
    n348 --> n349
    class n349 leafNode
    n350[source]
    n348 --> n350
    class n350 leafNode
    n351[lithium]
    n329 --> n351
    class n351 normalNode
    n352[value]
    n351 --> n352
    class n352 leafNode
    n353[source]
    n351 --> n353
    class n353 leafNode
    n354[carbon]
    n329 --> n354
    class n354 normalNode
    n355[value]
    n354 --> n355
    class n355 leafNode
    n356[source]
    n354 --> n356
    class n356 leafNode
    n357[nitrogen]
    n329 --> n357
    class n357 normalNode
    n358[value]
    n357 --> n358
    class n358 leafNode
    n359[source]
    n357 --> n359
    class n359 leafNode
    n360[neon]
    n329 --> n360
    class n360 normalNode
    n361[value]
    n360 --> n361
    class n361 leafNode
    n362[source]
    n360 --> n362
    class n362 leafNode
    n363[argon]
    n329 --> n363
    class n363 normalNode
    n364[value]
    n363 --> n364
    class n364 leafNode
    n365[source]
    n363 --> n365
    class n365 leafNode
    n366[xenon]
    n329 --> n366
    class n366 normalNode
    n367[value]
    n366 --> n367
    class n367 leafNode
    n368[source]
    n366 --> n368
    class n368 leafNode
    n369[oxygen]
    n329 --> n369
    class n369 normalNode
    n370[value]
    n369 --> n370
    class n370 leafNode
    n371[source]
    n369 --> n371
    class n371 leafNode
    n372[tungsten]
    n329 --> n372
    class n372 normalNode
    n373[value]
    n372 --> n373
    class n373 leafNode
    n374[source]
    n372 --> n374
    class n374 leafNode
    n375[iron]
    n329 --> n375
    class n375 normalNode
    n376[value]
    n375 --> n376
    class n376 leafNode
    n377[source]
    n375 --> n377
    class n377 leafNode
    n378[krypton]
    n329 --> n378
    class n378 normalNode
    n379[value]
    n378 --> n379
    class n379 leafNode
    n380[source]
    n378 --> n380
    class n380 leafNode
    n381[q]
    n249 --> n381
    class n381 normalNode
    n382[value]
    n381 --> n382
    class n382 leafNode
    n383[source]
    n381 --> n383
    class n383 leafNode
    n384[magnetic_shear]
    n249 --> n384
    class n384 normalNode
    n385[value]
    n384 --> n385
    class n385 leafNode
    n386[source]
    n384 --> n386
    class n386 leafNode
    n387[b_field_tor]
    n249 --> n387
    class n387 normalNode
    n388[value]
    n387 --> n388
    class n388 leafNode
    n389[source]
    n387 --> n389
    class n389 leafNode
    n390[b_field_phi]
    n249 --> n390
    class n390 normalNode
    n391[value]
    n390 --> n391
    class n391 leafNode
    n392[source]
    n390 --> n392
    class n392 leafNode
    n393[e_field_parallel]
    n249 --> n393
    class n393 normalNode
    n394[value]
    n393 --> n394
    class n394 leafNode
    n395[source]
    n393 --> n395
    class n395 leafNode
    n396(separatrix)
    n248 --> n396
    class n396 complexNode
    n397[position]
    n396 --> n397
    class n397 normalNode
    n398[rho_tor_norm]
    n397 --> n398
    class n398 leafNode
    n399[rho_tor]
    n397 --> n399
    class n399 leafNode
    n400[psi]
    n397 --> n400
    class n400 leafNode
    n401[t_e]
    n396 --> n401
    class n401 normalNode
    n402[value]
    n401 --> n402
    class n402 leafNode
    n403[source]
    n401 --> n403
    class n403 leafNode
    n404[t_i_average]
    n396 --> n404
    class n404 normalNode
    n405[value]
    n404 --> n405
    class n405 leafNode
    n406[source]
    n404 --> n406
    class n406 leafNode
    n407[n_e]
    n396 --> n407
    class n407 normalNode
    n408[value]
    n407 --> n408
    class n408 leafNode
    n409[source]
    n407 --> n409
    class n409 leafNode
    n410(n_i)
    n396 --> n410
    class n410 complexNode
    n411[hydrogen]
    n410 --> n411
    class n411 normalNode
    n412[value]
    n411 --> n412
    class n412 leafNode
    n413[source]
    n411 --> n413
    class n413 leafNode
    n414[deuterium]
    n410 --> n414
    class n414 normalNode
    n415[value]
    n414 --> n415
    class n415 leafNode
    n416[source]
    n414 --> n416
    class n416 leafNode
    n417[tritium]
    n410 --> n417
    class n417 normalNode
    n418[value]
    n417 --> n418
    class n418 leafNode
    n419[source]
    n417 --> n419
    class n419 leafNode
    n420[deuterium_tritium]
    n410 --> n420
    class n420 normalNode
    n421[value]
    n420 --> n421
    class n421 leafNode
    n422[source]
    n420 --> n422
    class n422 leafNode
    n423[helium_3]
    n410 --> n423
    class n423 normalNode
    n424[value]
    n423 --> n424
    class n424 leafNode
    n425[source]
    n423 --> n425
    class n425 leafNode
    n426[helium_4]
    n410 --> n426
    class n426 normalNode
    n427[value]
    n426 --> n427
    class n427 leafNode
    n428[source]
    n426 --> n428
    class n428 leafNode
    n429[beryllium]
    n410 --> n429
    class n429 normalNode
    n430[value]
    n429 --> n430
    class n430 leafNode
    n431[source]
    n429 --> n431
    class n431 leafNode
    n432[boron]
    n410 --> n432
    class n432 normalNode
    n433[value]
    n432 --> n433
    class n433 leafNode
    n434[source]
    n432 --> n434
    class n434 leafNode
    n435[lithium]
    n410 --> n435
    class n435 normalNode
    n436[value]
    n435 --> n436
    class n436 leafNode
    n437[source]
    n435 --> n437
    class n437 leafNode
    n438[carbon]
    n410 --> n438
    class n438 normalNode
    n439[value]
    n438 --> n439
    class n439 leafNode
    n440[source]
    n438 --> n440
    class n440 leafNode
    n441[nitrogen]
    n410 --> n441
    class n441 normalNode
    n442[value]
    n441 --> n442
    class n442 leafNode
    n443[source]
    n441 --> n443
    class n443 leafNode
    n444[neon]
    n410 --> n444
    class n444 normalNode
    n445[value]
    n444 --> n445
    class n445 leafNode
    n446[source]
    n444 --> n446
    class n446 leafNode
    n447[argon]
    n410 --> n447
    class n447 normalNode
    n448[value]
    n447 --> n448
    class n448 leafNode
    n449[source]
    n447 --> n449
    class n449 leafNode
    n450[xenon]
    n410 --> n450
    class n450 normalNode
    n451[value]
    n450 --> n451
    class n451 leafNode
    n452[source]
    n450 --> n452
    class n452 leafNode
    n453[oxygen]
    n410 --> n453
    class n453 normalNode
    n454[value]
    n453 --> n454
    class n454 leafNode
    n455[source]
    n453 --> n455
    class n455 leafNode
    n456[tungsten]
    n410 --> n456
    class n456 normalNode
    n457[value]
    n456 --> n457
    class n457 leafNode
    n458[source]
    n456 --> n458
    class n458 leafNode
    n459[iron]
    n410 --> n459
    class n459 normalNode
    n460[value]
    n459 --> n460
    class n460 leafNode
    n461[source]
    n459 --> n461
    class n461 leafNode
    n462[krypton]
    n410 --> n462
    class n462 normalNode
    n463[value]
    n462 --> n463
    class n463 leafNode
    n464[source]
    n462 --> n464
    class n464 leafNode
    n465[n_i_total]
    n396 --> n465
    class n465 normalNode
    n466[value]
    n465 --> n466
    class n466 leafNode
    n467[source]
    n465 --> n467
    class n467 leafNode
    n468[zeff]
    n396 --> n468
    class n468 normalNode
    n469[value]
    n468 --> n469
    class n469 leafNode
    n470[source]
    n468 --> n470
    class n470 leafNode
    n471[momentum_phi]
    n396 --> n471
    class n471 normalNode
    n472[value]
    n471 --> n472
    class n472 leafNode
    n473[source]
    n471 --> n473
    class n473 leafNode
    n474(velocity_phi)
    n396 --> n474
    class n474 complexNode
    n475[hydrogen]
    n474 --> n475
    class n475 normalNode
    n476[value]
    n475 --> n476
    class n476 leafNode
    n477[source]
    n475 --> n477
    class n477 leafNode
    n478[deuterium]
    n474 --> n478
    class n478 normalNode
    n479[value]
    n478 --> n479
    class n479 leafNode
    n480[source]
    n478 --> n480
    class n480 leafNode
    n481[tritium]
    n474 --> n481
    class n481 normalNode
    n482[value]
    n481 --> n482
    class n482 leafNode
    n483[source]
    n481 --> n483
    class n483 leafNode
    n484[deuterium_tritium]
    n474 --> n484
    class n484 normalNode
    n485[value]
    n484 --> n485
    class n485 leafNode
    n486[source]
    n484 --> n486
    class n486 leafNode
    n487[helium_3]
    n474 --> n487
    class n487 normalNode
    n488[value]
    n487 --> n488
    class n488 leafNode
    n489[source]
    n487 --> n489
    class n489 leafNode
    n490[helium_4]
    n474 --> n490
    class n490 normalNode
    n491[value]
    n490 --> n491
    class n491 leafNode
    n492[source]
    n490 --> n492
    class n492 leafNode
    n493[beryllium]
    n474 --> n493
    class n493 normalNode
    n494[value]
    n493 --> n494
    class n494 leafNode
    n495[source]
    n493 --> n495
    class n495 leafNode
    n496[lithium]
    n474 --> n496
    class n496 normalNode
    n497[value]
    n496 --> n497
    class n497 leafNode
    n498[source]
    n496 --> n498
    class n498 leafNode
    n499[carbon]
    n474 --> n499
    class n499 normalNode
    n500[value]
    n499 --> n500
    class n500 leafNode
    n501[source]
    n499 --> n501
    class n501 leafNode
    n502[nitrogen]
    n474 --> n502
    class n502 normalNode
    n503[value]
    n502 --> n503
    class n503 leafNode
    n504[source]
    n502 --> n504
    class n504 leafNode
    n505[neon]
    n474 --> n505
    class n505 normalNode
    n506[value]
    n505 --> n506
    class n506 leafNode
    n507[source]
    n505 --> n507
    class n507 leafNode
    n508[argon]
    n474 --> n508
    class n508 normalNode
    n509[value]
    n508 --> n509
    class n509 leafNode
    n510[source]
    n508 --> n510
    class n510 leafNode
    n511[xenon]
    n474 --> n511
    class n511 normalNode
    n512[value]
    n511 --> n512
    class n512 leafNode
    n513[source]
    n511 --> n513
    class n513 leafNode
    n514[oxygen]
    n474 --> n514
    class n514 normalNode
    n515[value]
    n514 --> n515
    class n515 leafNode
    n516[source]
    n514 --> n516
    class n516 leafNode
    n517[tungsten]
    n474 --> n517
    class n517 normalNode
    n518[value]
    n517 --> n518
    class n518 leafNode
    n519[source]
    n517 --> n519
    class n519 leafNode
    n520[iron]
    n474 --> n520
    class n520 normalNode
    n521[value]
    n520 --> n521
    class n521 leafNode
    n522[source]
    n520 --> n522
    class n522 leafNode
    n523[krypton]
    n474 --> n523
    class n523 normalNode
    n524[value]
    n523 --> n524
    class n524 leafNode
    n525[source]
    n523 --> n525
    class n525 leafNode
    n526[q]
    n396 --> n526
    class n526 normalNode
    n527[value]
    n526 --> n527
    class n527 leafNode
    n528[source]
    n526 --> n528
    class n528 leafNode
    n529[magnetic_shear]
    n396 --> n529
    class n529 normalNode
    n530[value]
    n529 --> n530
    class n530 leafNode
    n531[source]
    n529 --> n531
    class n531 leafNode
    n532[e_field_parallel]
    n396 --> n532
    class n532 normalNode
    n533[value]
    n532 --> n533
    class n533 leafNode
    n534[source]
    n532 --> n534
    class n534 leafNode
    n535(separatrix_average)
    n248 --> n535
    class n535 complexNode
    n536[position]
    n535 --> n536
    class n536 normalNode
    n537[rho_tor_norm]
    n536 --> n537
    class n537 leafNode
    n538[rho_tor]
    n536 --> n538
    class n538 leafNode
    n539[psi]
    n536 --> n539
    class n539 leafNode
    n540[t_e]
    n535 --> n540
    class n540 normalNode
    n541[value]
    n540 --> n541
    class n541 leafNode
    n542[source]
    n540 --> n542
    class n542 leafNode
    n543[t_i_average]
    n535 --> n543
    class n543 normalNode
    n544[value]
    n543 --> n544
    class n544 leafNode
    n545[source]
    n543 --> n545
    class n545 leafNode
    n546[n_e]
    n535 --> n546
    class n546 normalNode
    n547[value]
    n546 --> n547
    class n547 leafNode
    n548[source]
    n546 --> n548
    class n548 leafNode
    n549(n_i)
    n535 --> n549
    class n549 complexNode
    n550[hydrogen]
    n549 --> n550
    class n550 normalNode
    n551[value]
    n550 --> n551
    class n551 leafNode
    n552[source]
    n550 --> n552
    class n552 leafNode
    n553[deuterium]
    n549 --> n553
    class n553 normalNode
    n554[value]
    n553 --> n554
    class n554 leafNode
    n555[source]
    n553 --> n555
    class n555 leafNode
    n556[tritium]
    n549 --> n556
    class n556 normalNode
    n557[value]
    n556 --> n557
    class n557 leafNode
    n558[source]
    n556 --> n558
    class n558 leafNode
    n559[deuterium_tritium]
    n549 --> n559
    class n559 normalNode
    n560[value]
    n559 --> n560
    class n560 leafNode
    n561[source]
    n559 --> n561
    class n561 leafNode
    n562[helium_3]
    n549 --> n562
    class n562 normalNode
    n563[value]
    n562 --> n563
    class n563 leafNode
    n564[source]
    n562 --> n564
    class n564 leafNode
    n565[helium_4]
    n549 --> n565
    class n565 normalNode
    n566[value]
    n565 --> n566
    class n566 leafNode
    n567[source]
    n565 --> n567
    class n567 leafNode
    n568[beryllium]
    n549 --> n568
    class n568 normalNode
    n569[value]
    n568 --> n569
    class n569 leafNode
    n570[source]
    n568 --> n570
    class n570 leafNode
    n571[boron]
    n549 --> n571
    class n571 normalNode
    n572[value]
    n571 --> n572
    class n572 leafNode
    n573[source]
    n571 --> n573
    class n573 leafNode
    n574[lithium]
    n549 --> n574
    class n574 normalNode
    n575[value]
    n574 --> n575
    class n575 leafNode
    n576[source]
    n574 --> n576
    class n576 leafNode
    n577[carbon]
    n549 --> n577
    class n577 normalNode
    n578[value]
    n577 --> n578
    class n578 leafNode
    n579[source]
    n577 --> n579
    class n579 leafNode
    n580[nitrogen]
    n549 --> n580
    class n580 normalNode
    n581[value]
    n580 --> n581
    class n581 leafNode
    n582[source]
    n580 --> n582
    class n582 leafNode
    n583[neon]
    n549 --> n583
    class n583 normalNode
    n584[value]
    n583 --> n584
    class n584 leafNode
    n585[source]
    n583 --> n585
    class n585 leafNode
    n586[argon]
    n549 --> n586
    class n586 normalNode
    n587[value]
    n586 --> n587
    class n587 leafNode
    n588[source]
    n586 --> n588
    class n588 leafNode
    n589[xenon]
    n549 --> n589
    class n589 normalNode
    n590[value]
    n589 --> n590
    class n590 leafNode
    n591[source]
    n589 --> n591
    class n591 leafNode
    n592[oxygen]
    n549 --> n592
    class n592 normalNode
    n593[value]
    n592 --> n593
    class n593 leafNode
    n594[source]
    n592 --> n594
    class n594 leafNode
    n595[tungsten]
    n549 --> n595
    class n595 normalNode
    n596[value]
    n595 --> n596
    class n596 leafNode
    n597[source]
    n595 --> n597
    class n597 leafNode
    n598[iron]
    n549 --> n598
    class n598 normalNode
    n599[value]
    n598 --> n599
    class n599 leafNode
    n600[source]
    n598 --> n600
    class n600 leafNode
    n601[krypton]
    n549 --> n601
    class n601 normalNode
    n602[value]
    n601 --> n602
    class n602 leafNode
    n603[source]
    n601 --> n603
    class n603 leafNode
    n604[n_i_total]
    n535 --> n604
    class n604 normalNode
    n605[value]
    n604 --> n605
    class n605 leafNode
    n606[source]
    n604 --> n606
    class n606 leafNode
    n607[zeff]
    n535 --> n607
    class n607 normalNode
    n608[value]
    n607 --> n608
    class n608 leafNode
    n609[source]
    n607 --> n609
    class n609 leafNode
    n610[momentum_phi]
    n535 --> n610
    class n610 normalNode
    n611[value]
    n610 --> n611
    class n611 leafNode
    n612[source]
    n610 --> n612
    class n612 leafNode
    n613(velocity_phi)
    n535 --> n613
    class n613 complexNode
    n614[hydrogen]
    n613 --> n614
    class n614 normalNode
    n615[value]
    n614 --> n615
    class n615 leafNode
    n616[source]
    n614 --> n616
    class n616 leafNode
    n617[deuterium]
    n613 --> n617
    class n617 normalNode
    n618[value]
    n617 --> n618
    class n618 leafNode
    n619[source]
    n617 --> n619
    class n619 leafNode
    n620[tritium]
    n613 --> n620
    class n620 normalNode
    n621[value]
    n620 --> n621
    class n621 leafNode
    n622[source]
    n620 --> n622
    class n622 leafNode
    n623[deuterium_tritium]
    n613 --> n623
    class n623 normalNode
    n624[value]
    n623 --> n624
    class n624 leafNode
    n625[source]
    n623 --> n625
    class n625 leafNode
    n626[helium_3]
    n613 --> n626
    class n626 normalNode
    n627[value]
    n626 --> n627
    class n627 leafNode
    n628[source]
    n626 --> n628
    class n628 leafNode
    n629[helium_4]
    n613 --> n629
    class n629 normalNode
    n630[value]
    n629 --> n630
    class n630 leafNode
    n631[source]
    n629 --> n631
    class n631 leafNode
    n632[beryllium]
    n613 --> n632
    class n632 normalNode
    n633[value]
    n632 --> n633
    class n633 leafNode
    n634[source]
    n632 --> n634
    class n634 leafNode
    n635[lithium]
    n613 --> n635
    class n635 normalNode
    n636[value]
    n635 --> n636
    class n636 leafNode
    n637[source]
    n635 --> n637
    class n637 leafNode
    n638[carbon]
    n613 --> n638
    class n638 normalNode
    n639[value]
    n638 --> n639
    class n639 leafNode
    n640[source]
    n638 --> n640
    class n640 leafNode
    n641[nitrogen]
    n613 --> n641
    class n641 normalNode
    n642[value]
    n641 --> n642
    class n642 leafNode
    n643[source]
    n641 --> n643
    class n643 leafNode
    n644[neon]
    n613 --> n644
    class n644 normalNode
    n645[value]
    n644 --> n645
    class n645 leafNode
    n646[source]
    n644 --> n646
    class n646 leafNode
    n647[argon]
    n613 --> n647
    class n647 normalNode
    n648[value]
    n647 --> n648
    class n648 leafNode
    n649[source]
    n647 --> n649
    class n649 leafNode
    n650[xenon]
    n613 --> n650
    class n650 normalNode
    n651[value]
    n650 --> n651
    class n651 leafNode
    n652[source]
    n650 --> n652
    class n652 leafNode
    n653[oxygen]
    n613 --> n653
    class n653 normalNode
    n654[value]
    n653 --> n654
    class n654 leafNode
    n655[source]
    n653 --> n655
    class n655 leafNode
    n656[tungsten]
    n613 --> n656
    class n656 normalNode
    n657[value]
    n656 --> n657
    class n657 leafNode
    n658[source]
    n656 --> n658
    class n658 leafNode
    n659[iron]
    n613 --> n659
    class n659 normalNode
    n660[value]
    n659 --> n660
    class n660 leafNode
    n661[source]
    n659 --> n661
    class n661 leafNode
    n662[krypton]
    n613 --> n662
    class n662 normalNode
    n663[value]
    n662 --> n663
    class n663 leafNode
    n664[source]
    n662 --> n664
    class n664 leafNode
    n665[q]
    n535 --> n665
    class n665 normalNode
    n666[value]
    n665 --> n666
    class n666 leafNode
    n667[source]
    n665 --> n667
    class n667 leafNode
    n668[magnetic_shear]
    n535 --> n668
    class n668 normalNode
    n669[value]
    n668 --> n669
    class n669 leafNode
    n670[source]
    n668 --> n670
    class n670 leafNode
    n671[e_field_parallel]
    n535 --> n671
    class n671 normalNode
    n672[value]
    n671 --> n672
    class n672 leafNode
    n673[source]
    n671 --> n673
    class n673 leafNode
    n674(pedestal)
    n248 --> n674
    class n674 complexNode
    n675[position]
    n674 --> n675
    class n675 normalNode
    n676[rho_tor_norm]
    n675 --> n676
    class n676 leafNode
    n677[rho_tor]
    n675 --> n677
    class n677 leafNode
    n678[psi]
    n675 --> n678
    class n678 leafNode
    n679[t_e]
    n674 --> n679
    class n679 normalNode
    n680[value]
    n679 --> n680
    class n680 leafNode
    n681[source]
    n679 --> n681
    class n681 leafNode
    n682[t_i_average]
    n674 --> n682
    class n682 normalNode
    n683[value]
    n682 --> n683
    class n683 leafNode
    n684[source]
    n682 --> n684
    class n684 leafNode
    n685[n_e]
    n674 --> n685
    class n685 normalNode
    n686[value]
    n685 --> n686
    class n686 leafNode
    n687[source]
    n685 --> n687
    class n687 leafNode
    n688(n_i)
    n674 --> n688
    class n688 complexNode
    n689[hydrogen]
    n688 --> n689
    class n689 normalNode
    n690[value]
    n689 --> n690
    class n690 leafNode
    n691[source]
    n689 --> n691
    class n691 leafNode
    n692[deuterium]
    n688 --> n692
    class n692 normalNode
    n693[value]
    n692 --> n693
    class n693 leafNode
    n694[source]
    n692 --> n694
    class n694 leafNode
    n695[tritium]
    n688 --> n695
    class n695 normalNode
    n696[value]
    n695 --> n696
    class n696 leafNode
    n697[source]
    n695 --> n697
    class n697 leafNode
    n698[deuterium_tritium]
    n688 --> n698
    class n698 normalNode
    n699[value]
    n698 --> n699
    class n699 leafNode
    n700[source]
    n698 --> n700
    class n700 leafNode
    n701[helium_3]
    n688 --> n701
    class n701 normalNode
    n702[value]
    n701 --> n702
    class n702 leafNode
    n703[source]
    n701 --> n703
    class n703 leafNode
    n704[helium_4]
    n688 --> n704
    class n704 normalNode
    n705[value]
    n704 --> n705
    class n705 leafNode
    n706[source]
    n704 --> n706
    class n706 leafNode
    n707[beryllium]
    n688 --> n707
    class n707 normalNode
    n708[value]
    n707 --> n708
    class n708 leafNode
    n709[source]
    n707 --> n709
    class n709 leafNode
    n710[boron]
    n688 --> n710
    class n710 normalNode
    n711[value]
    n710 --> n711
    class n711 leafNode
    n712[source]
    n710 --> n712
    class n712 leafNode
    n713[lithium]
    n688 --> n713
    class n713 normalNode
    n714[value]
    n713 --> n714
    class n714 leafNode
    n715[source]
    n713 --> n715
    class n715 leafNode
    n716[carbon]
    n688 --> n716
    class n716 normalNode
    n717[value]
    n716 --> n717
    class n717 leafNode
    n718[source]
    n716 --> n718
    class n718 leafNode
    n719[nitrogen]
    n688 --> n719
    class n719 normalNode
    n720[value]
    n719 --> n720
    class n720 leafNode
    n721[source]
    n719 --> n721
    class n721 leafNode
    n722[neon]
    n688 --> n722
    class n722 normalNode
    n723[value]
    n722 --> n723
    class n723 leafNode
    n724[source]
    n722 --> n724
    class n724 leafNode
    n725[argon]
    n688 --> n725
    class n725 normalNode
    n726[value]
    n725 --> n726
    class n726 leafNode
    n727[source]
    n725 --> n727
    class n727 leafNode
    n728[xenon]
    n688 --> n728
    class n728 normalNode
    n729[value]
    n728 --> n729
    class n729 leafNode
    n730[source]
    n728 --> n730
    class n730 leafNode
    n731[oxygen]
    n688 --> n731
    class n731 normalNode
    n732[value]
    n731 --> n732
    class n732 leafNode
    n733[source]
    n731 --> n733
    class n733 leafNode
    n734[tungsten]
    n688 --> n734
    class n734 normalNode
    n735[value]
    n734 --> n735
    class n735 leafNode
    n736[source]
    n734 --> n736
    class n736 leafNode
    n737[iron]
    n688 --> n737
    class n737 normalNode
    n738[value]
    n737 --> n738
    class n738 leafNode
    n739[source]
    n737 --> n739
    class n739 leafNode
    n740[krypton]
    n688 --> n740
    class n740 normalNode
    n741[value]
    n740 --> n741
    class n741 leafNode
    n742[source]
    n740 --> n742
    class n742 leafNode
    n743[n_i_total]
    n674 --> n743
    class n743 normalNode
    n744[value]
    n743 --> n744
    class n744 leafNode
    n745[source]
    n743 --> n745
    class n745 leafNode
    n746[zeff]
    n674 --> n746
    class n746 normalNode
    n747[value]
    n746 --> n747
    class n747 leafNode
    n748[source]
    n746 --> n748
    class n748 leafNode
    n749[momentum_phi]
    n674 --> n749
    class n749 normalNode
    n750[value]
    n749 --> n750
    class n750 leafNode
    n751[source]
    n749 --> n751
    class n751 leafNode
    n752(velocity_phi)
    n674 --> n752
    class n752 complexNode
    n753[hydrogen]
    n752 --> n753
    class n753 normalNode
    n754[value]
    n753 --> n754
    class n754 leafNode
    n755[source]
    n753 --> n755
    class n755 leafNode
    n756[deuterium]
    n752 --> n756
    class n756 normalNode
    n757[value]
    n756 --> n757
    class n757 leafNode
    n758[source]
    n756 --> n758
    class n758 leafNode
    n759[tritium]
    n752 --> n759
    class n759 normalNode
    n760[value]
    n759 --> n760
    class n760 leafNode
    n761[source]
    n759 --> n761
    class n761 leafNode
    n762[deuterium_tritium]
    n752 --> n762
    class n762 normalNode
    n763[value]
    n762 --> n763
    class n763 leafNode
    n764[source]
    n762 --> n764
    class n764 leafNode
    n765[helium_3]
    n752 --> n765
    class n765 normalNode
    n766[value]
    n765 --> n766
    class n766 leafNode
    n767[source]
    n765 --> n767
    class n767 leafNode
    n768[helium_4]
    n752 --> n768
    class n768 normalNode
    n769[value]
    n768 --> n769
    class n769 leafNode
    n770[source]
    n768 --> n770
    class n770 leafNode
    n771[beryllium]
    n752 --> n771
    class n771 normalNode
    n772[value]
    n771 --> n772
    class n772 leafNode
    n773[source]
    n771 --> n773
    class n773 leafNode
    n774[lithium]
    n752 --> n774
    class n774 normalNode
    n775[value]
    n774 --> n775
    class n775 leafNode
    n776[source]
    n774 --> n776
    class n776 leafNode
    n777[carbon]
    n752 --> n777
    class n777 normalNode
    n778[value]
    n777 --> n778
    class n778 leafNode
    n779[source]
    n777 --> n779
    class n779 leafNode
    n780[nitrogen]
    n752 --> n780
    class n780 normalNode
    n781[value]
    n780 --> n781
    class n781 leafNode
    n782[source]
    n780 --> n782
    class n782 leafNode
    n783[neon]
    n752 --> n783
    class n783 normalNode
    n784[value]
    n783 --> n784
    class n784 leafNode
    n785[source]
    n783 --> n785
    class n785 leafNode
    n786[argon]
    n752 --> n786
    class n786 normalNode
    n787[value]
    n786 --> n787
    class n787 leafNode
    n788[source]
    n786 --> n788
    class n788 leafNode
    n789[xenon]
    n752 --> n789
    class n789 normalNode
    n790[value]
    n789 --> n790
    class n790 leafNode
    n791[source]
    n789 --> n791
    class n791 leafNode
    n792[oxygen]
    n752 --> n792
    class n792 normalNode
    n793[value]
    n792 --> n793
    class n793 leafNode
    n794[source]
    n792 --> n794
    class n794 leafNode
    n795[tungsten]
    n752 --> n795
    class n795 normalNode
    n796[value]
    n795 --> n796
    class n796 leafNode
    n797[source]
    n795 --> n797
    class n797 leafNode
    n798[iron]
    n752 --> n798
    class n798 normalNode
    n799[value]
    n798 --> n799
    class n799 leafNode
    n800[source]
    n798 --> n800
    class n800 leafNode
    n801[krypton]
    n752 --> n801
    class n801 normalNode
    n802[value]
    n801 --> n802
    class n802 leafNode
    n803[source]
    n801 --> n803
    class n803 leafNode
    n804[q]
    n674 --> n804
    class n804 normalNode
    n805[value]
    n804 --> n805
    class n805 leafNode
    n806[source]
    n804 --> n806
    class n806 leafNode
    n807[magnetic_shear]
    n674 --> n807
    class n807 normalNode
    n808[value]
    n807 --> n808
    class n808 leafNode
    n809[source]
    n807 --> n809
    class n809 leafNode
    n810[e_field_parallel]
    n674 --> n810
    class n810 normalNode
    n811[value]
    n810 --> n811
    class n811 leafNode
    n812[source]
    n810 --> n812
    class n812 leafNode
    n813(itb)
    n248 --> n813
    class n813 complexNode
    n814[position]
    n813 --> n814
    class n814 normalNode
    n815[rho_tor_norm]
    n814 --> n815
    class n815 leafNode
    n816[rho_tor]
    n814 --> n816
    class n816 leafNode
    n817[psi]
    n814 --> n817
    class n817 leafNode
    n818[t_e]
    n813 --> n818
    class n818 normalNode
    n819[value]
    n818 --> n819
    class n819 leafNode
    n820[source]
    n818 --> n820
    class n820 leafNode
    n821[t_i_average]
    n813 --> n821
    class n821 normalNode
    n822[value]
    n821 --> n822
    class n822 leafNode
    n823[source]
    n821 --> n823
    class n823 leafNode
    n824[n_e]
    n813 --> n824
    class n824 normalNode
    n825[value]
    n824 --> n825
    class n825 leafNode
    n826[source]
    n824 --> n826
    class n826 leafNode
    n827(n_i)
    n813 --> n827
    class n827 complexNode
    n828[hydrogen]
    n827 --> n828
    class n828 normalNode
    n829[value]
    n828 --> n829
    class n829 leafNode
    n830[source]
    n828 --> n830
    class n830 leafNode
    n831[deuterium]
    n827 --> n831
    class n831 normalNode
    n832[value]
    n831 --> n832
    class n832 leafNode
    n833[source]
    n831 --> n833
    class n833 leafNode
    n834[tritium]
    n827 --> n834
    class n834 normalNode
    n835[value]
    n834 --> n835
    class n835 leafNode
    n836[source]
    n834 --> n836
    class n836 leafNode
    n837[deuterium_tritium]
    n827 --> n837
    class n837 normalNode
    n838[value]
    n837 --> n838
    class n838 leafNode
    n839[source]
    n837 --> n839
    class n839 leafNode
    n840[helium_3]
    n827 --> n840
    class n840 normalNode
    n841[value]
    n840 --> n841
    class n841 leafNode
    n842[source]
    n840 --> n842
    class n842 leafNode
    n843[helium_4]
    n827 --> n843
    class n843 normalNode
    n844[value]
    n843 --> n844
    class n844 leafNode
    n845[source]
    n843 --> n845
    class n845 leafNode
    n846[beryllium]
    n827 --> n846
    class n846 normalNode
    n847[value]
    n846 --> n847
    class n847 leafNode
    n848[source]
    n846 --> n848
    class n848 leafNode
    n849[boron]
    n827 --> n849
    class n849 normalNode
    n850[value]
    n849 --> n850
    class n850 leafNode
    n851[source]
    n849 --> n851
    class n851 leafNode
    n852[lithium]
    n827 --> n852
    class n852 normalNode
    n853[value]
    n852 --> n853
    class n853 leafNode
    n854[source]
    n852 --> n854
    class n854 leafNode
    n855[carbon]
    n827 --> n855
    class n855 normalNode
    n856[value]
    n855 --> n856
    class n856 leafNode
    n857[source]
    n855 --> n857
    class n857 leafNode
    n858[nitrogen]
    n827 --> n858
    class n858 normalNode
    n859[value]
    n858 --> n859
    class n859 leafNode
    n860[source]
    n858 --> n860
    class n860 leafNode
    n861[neon]
    n827 --> n861
    class n861 normalNode
    n862[value]
    n861 --> n862
    class n862 leafNode
    n863[source]
    n861 --> n863
    class n863 leafNode
    n864[argon]
    n827 --> n864
    class n864 normalNode
    n865[value]
    n864 --> n865
    class n865 leafNode
    n866[source]
    n864 --> n866
    class n866 leafNode
    n867[xenon]
    n827 --> n867
    class n867 normalNode
    n868[value]
    n867 --> n868
    class n868 leafNode
    n869[source]
    n867 --> n869
    class n869 leafNode
    n870[oxygen]
    n827 --> n870
    class n870 normalNode
    n871[value]
    n870 --> n871
    class n871 leafNode
    n872[source]
    n870 --> n872
    class n872 leafNode
    n873[tungsten]
    n827 --> n873
    class n873 normalNode
    n874[value]
    n873 --> n874
    class n874 leafNode
    n875[source]
    n873 --> n875
    class n875 leafNode
    n876[iron]
    n827 --> n876
    class n876 normalNode
    n877[value]
    n876 --> n877
    class n877 leafNode
    n878[source]
    n876 --> n878
    class n878 leafNode
    n879[krypton]
    n827 --> n879
    class n879 normalNode
    n880[value]
    n879 --> n880
    class n880 leafNode
    n881[source]
    n879 --> n881
    class n881 leafNode
    n882[n_i_total]
    n813 --> n882
    class n882 normalNode
    n883[value]
    n882 --> n883
    class n883 leafNode
    n884[source]
    n882 --> n884
    class n884 leafNode
    n885[zeff]
    n813 --> n885
    class n885 normalNode
    n886[value]
    n885 --> n886
    class n886 leafNode
    n887[source]
    n885 --> n887
    class n887 leafNode
    n888[momentum_phi]
    n813 --> n888
    class n888 normalNode
    n889[value]
    n888 --> n889
    class n889 leafNode
    n890[source]
    n888 --> n890
    class n890 leafNode
    n891(velocity_phi)
    n813 --> n891
    class n891 complexNode
    n892[hydrogen]
    n891 --> n892
    class n892 normalNode
    n893[value]
    n892 --> n893
    class n893 leafNode
    n894[source]
    n892 --> n894
    class n894 leafNode
    n895[deuterium]
    n891 --> n895
    class n895 normalNode
    n896[value]
    n895 --> n896
    class n896 leafNode
    n897[source]
    n895 --> n897
    class n897 leafNode
    n898[tritium]
    n891 --> n898
    class n898 normalNode
    n899[value]
    n898 --> n899
    class n899 leafNode
    n900[source]
    n898 --> n900
    class n900 leafNode
    n901[deuterium_tritium]
    n891 --> n901
    class n901 normalNode
    n902[value]
    n901 --> n902
    class n902 leafNode
    n903[source]
    n901 --> n903
    class n903 leafNode
    n904[helium_3]
    n891 --> n904
    class n904 normalNode
    n905[value]
    n904 --> n905
    class n905 leafNode
    n906[source]
    n904 --> n906
    class n906 leafNode
    n907[helium_4]
    n891 --> n907
    class n907 normalNode
    n908[value]
    n907 --> n908
    class n908 leafNode
    n909[source]
    n907 --> n909
    class n909 leafNode
    n910[beryllium]
    n891 --> n910
    class n910 normalNode
    n911[value]
    n910 --> n911
    class n911 leafNode
    n912[source]
    n910 --> n912
    class n912 leafNode
    n913[lithium]
    n891 --> n913
    class n913 normalNode
    n914[value]
    n913 --> n914
    class n914 leafNode
    n915[source]
    n913 --> n915
    class n915 leafNode
    n916[carbon]
    n891 --> n916
    class n916 normalNode
    n917[value]
    n916 --> n917
    class n917 leafNode
    n918[source]
    n916 --> n918
    class n918 leafNode
    n919[nitrogen]
    n891 --> n919
    class n919 normalNode
    n920[value]
    n919 --> n920
    class n920 leafNode
    n921[source]
    n919 --> n921
    class n921 leafNode
    n922[neon]
    n891 --> n922
    class n922 normalNode
    n923[value]
    n922 --> n923
    class n923 leafNode
    n924[source]
    n922 --> n924
    class n924 leafNode
    n925[argon]
    n891 --> n925
    class n925 normalNode
    n926[value]
    n925 --> n926
    class n926 leafNode
    n927[source]
    n925 --> n927
    class n927 leafNode
    n928[xenon]
    n891 --> n928
    class n928 normalNode
    n929[value]
    n928 --> n929
    class n929 leafNode
    n930[source]
    n928 --> n930
    class n930 leafNode
    n931[oxygen]
    n891 --> n931
    class n931 normalNode
    n932[value]
    n931 --> n932
    class n932 leafNode
    n933[source]
    n931 --> n933
    class n933 leafNode
    n934[tungsten]
    n891 --> n934
    class n934 normalNode
    n935[value]
    n934 --> n935
    class n935 leafNode
    n936[source]
    n934 --> n936
    class n936 leafNode
    n937[iron]
    n891 --> n937
    class n937 normalNode
    n938[value]
    n937 --> n938
    class n938 leafNode
    n939[source]
    n937 --> n939
    class n939 leafNode
    n940[krypton]
    n891 --> n940
    class n940 normalNode
    n941[value]
    n940 --> n941
    class n941 leafNode
    n942[source]
    n940 --> n942
    class n942 leafNode
    n943[q]
    n813 --> n943
    class n943 normalNode
    n944[value]
    n943 --> n944
    class n944 leafNode
    n945[source]
    n943 --> n945
    class n945 leafNode
    n946[magnetic_shear]
    n813 --> n946
    class n946 normalNode
    n947[value]
    n946 --> n947
    class n947 leafNode
    n948[source]
    n946 --> n948
    class n948 leafNode
    n949[e_field_parallel]
    n813 --> n949
    class n949 normalNode
    n950[value]
    n949 --> n950
    class n950 leafNode
    n951[source]
    n949 --> n951
    class n951 leafNode
    n952(limiter)
    n248 --> n952
    class n952 complexNode
    n953[name]
    n952 --> n953
    class n953 normalNode
    n954[value]
    n953 --> n954
    class n954 leafNode
    n955[source]
    n953 --> n955
    class n955 leafNode
    n956[t_e]
    n952 --> n956
    class n956 normalNode
    n957[value]
    n956 --> n957
    class n957 leafNode
    n958[source]
    n956 --> n958
    class n958 leafNode
    n959[t_i_average]
    n952 --> n959
    class n959 normalNode
    n960[value]
    n959 --> n960
    class n960 leafNode
    n961[source]
    n959 --> n961
    class n961 leafNode
    n962[n_e]
    n952 --> n962
    class n962 normalNode
    n963[value]
    n962 --> n963
    class n963 leafNode
    n964[source]
    n962 --> n964
    class n964 leafNode
    n965(n_i)
    n952 --> n965
    class n965 complexNode
    n966[hydrogen]
    n965 --> n966
    class n966 normalNode
    n967[value]
    n966 --> n967
    class n967 leafNode
    n968[source]
    n966 --> n968
    class n968 leafNode
    n969[deuterium]
    n965 --> n969
    class n969 normalNode
    n970[value]
    n969 --> n970
    class n970 leafNode
    n971[source]
    n969 --> n971
    class n971 leafNode
    n972[tritium]
    n965 --> n972
    class n972 normalNode
    n973[value]
    n972 --> n973
    class n973 leafNode
    n974[source]
    n972 --> n974
    class n974 leafNode
    n975[deuterium_tritium]
    n965 --> n975
    class n975 normalNode
    n976[value]
    n975 --> n976
    class n976 leafNode
    n977[source]
    n975 --> n977
    class n977 leafNode
    n978[helium_3]
    n965 --> n978
    class n978 normalNode
    n979[value]
    n978 --> n979
    class n979 leafNode
    n980[source]
    n978 --> n980
    class n980 leafNode
    n981[helium_4]
    n965 --> n981
    class n981 normalNode
    n982[value]
    n981 --> n982
    class n982 leafNode
    n983[source]
    n981 --> n983
    class n983 leafNode
    n984[beryllium]
    n965 --> n984
    class n984 normalNode
    n985[value]
    n984 --> n985
    class n985 leafNode
    n986[source]
    n984 --> n986
    class n986 leafNode
    n987[boron]
    n965 --> n987
    class n987 normalNode
    n988[value]
    n987 --> n988
    class n988 leafNode
    n989[source]
    n987 --> n989
    class n989 leafNode
    n990[lithium]
    n965 --> n990
    class n990 normalNode
    n991[value]
    n990 --> n991
    class n991 leafNode
    n992[source]
    n990 --> n992
    class n992 leafNode
    n993[carbon]
    n965 --> n993
    class n993 normalNode
    n994[value]
    n993 --> n994
    class n994 leafNode
    n995[source]
    n993 --> n995
    class n995 leafNode
    n996[nitrogen]
    n965 --> n996
    class n996 normalNode
    n997[value]
    n996 --> n997
    class n997 leafNode
    n998[source]
    n996 --> n998
    class n998 leafNode
    n999[neon]
    n965 --> n999
    class n999 normalNode
    n1000[value]
    n999 --> n1000
    class n1000 leafNode
    n1001[source]
    n999 --> n1001
    class n1001 leafNode
    n1002[argon]
    n965 --> n1002
    class n1002 normalNode
    n1003[value]
    n1002 --> n1003
    class n1003 leafNode
    n1004[source]
    n1002 --> n1004
    class n1004 leafNode
    n1005[xenon]
    n965 --> n1005
    class n1005 normalNode
    n1006[value]
    n1005 --> n1006
    class n1006 leafNode
    n1007[source]
    n1005 --> n1007
    class n1007 leafNode
    n1008[oxygen]
    n965 --> n1008
    class n1008 normalNode
    n1009[value]
    n1008 --> n1009
    class n1009 leafNode
    n1010[source]
    n1008 --> n1010
    class n1010 leafNode
    n1011[tungsten]
    n965 --> n1011
    class n1011 normalNode
    n1012[value]
    n1011 --> n1012
    class n1012 leafNode
    n1013[source]
    n1011 --> n1013
    class n1013 leafNode
    n1014[iron]
    n965 --> n1014
    class n1014 normalNode
    n1015[value]
    n1014 --> n1015
    class n1015 leafNode
    n1016[source]
    n1014 --> n1016
    class n1016 leafNode
    n1017[krypton]
    n965 --> n1017
    class n1017 normalNode
    n1018[value]
    n1017 --> n1018
    class n1018 leafNode
    n1019[source]
    n1017 --> n1019
    class n1019 leafNode
    n1020[n_i_total]
    n952 --> n1020
    class n1020 normalNode
    n1021[value]
    n1020 --> n1021
    class n1021 leafNode
    n1022[source]
    n1020 --> n1022
    class n1022 leafNode
    n1023[zeff]
    n952 --> n1023
    class n1023 normalNode
    n1024[value]
    n1023 --> n1024
    class n1024 leafNode
    n1025[source]
    n1023 --> n1025
    class n1025 leafNode
    n1026[flux_expansion]
    n952 --> n1026
    class n1026 normalNode
    n1027[value]
    n1026 --> n1027
    class n1027 leafNode
    n1028[source]
    n1026 --> n1028
    class n1028 leafNode
    n1029[power_flux_peak]
    n952 --> n1029
    class n1029 normalNode
    n1030[value]
    n1029 --> n1030
    class n1030 leafNode
    n1031[source]
    n1029 --> n1031
    class n1031 leafNode
    n1032(divertor_target)
    n248 --> n1032
    class n1032 complexNode
    n1033[name]
    n1032 --> n1033
    class n1033 normalNode
    n1034[value]
    n1033 --> n1034
    class n1034 leafNode
    n1035[source]
    n1033 --> n1035
    class n1035 leafNode
    n1036[t_e]
    n1032 --> n1036
    class n1036 normalNode
    n1037[value]
    n1036 --> n1037
    class n1037 leafNode
    n1038[source]
    n1036 --> n1038
    class n1038 leafNode
    n1039[t_i_average]
    n1032 --> n1039
    class n1039 normalNode
    n1040[value]
    n1039 --> n1040
    class n1040 leafNode
    n1041[source]
    n1039 --> n1041
    class n1041 leafNode
    n1042[n_e]
    n1032 --> n1042
    class n1042 normalNode
    n1043[value]
    n1042 --> n1043
    class n1043 leafNode
    n1044[source]
    n1042 --> n1044
    class n1044 leafNode
    n1045(n_i)
    n1032 --> n1045
    class n1045 complexNode
    n1046[hydrogen]
    n1045 --> n1046
    class n1046 normalNode
    n1047[value]
    n1046 --> n1047
    class n1047 leafNode
    n1048[source]
    n1046 --> n1048
    class n1048 leafNode
    n1049[deuterium]
    n1045 --> n1049
    class n1049 normalNode
    n1050[value]
    n1049 --> n1050
    class n1050 leafNode
    n1051[source]
    n1049 --> n1051
    class n1051 leafNode
    n1052[tritium]
    n1045 --> n1052
    class n1052 normalNode
    n1053[value]
    n1052 --> n1053
    class n1053 leafNode
    n1054[source]
    n1052 --> n1054
    class n1054 leafNode
    n1055[deuterium_tritium]
    n1045 --> n1055
    class n1055 normalNode
    n1056[value]
    n1055 --> n1056
    class n1056 leafNode
    n1057[source]
    n1055 --> n1057
    class n1057 leafNode
    n1058[helium_3]
    n1045 --> n1058
    class n1058 normalNode
    n1059[value]
    n1058 --> n1059
    class n1059 leafNode
    n1060[source]
    n1058 --> n1060
    class n1060 leafNode
    n1061[helium_4]
    n1045 --> n1061
    class n1061 normalNode
    n1062[value]
    n1061 --> n1062
    class n1062 leafNode
    n1063[source]
    n1061 --> n1063
    class n1063 leafNode
    n1064[beryllium]
    n1045 --> n1064
    class n1064 normalNode
    n1065[value]
    n1064 --> n1065
    class n1065 leafNode
    n1066[source]
    n1064 --> n1066
    class n1066 leafNode
    n1067[boron]
    n1045 --> n1067
    class n1067 normalNode
    n1068[value]
    n1067 --> n1068
    class n1068 leafNode
    n1069[source]
    n1067 --> n1069
    class n1069 leafNode
    n1070[lithium]
    n1045 --> n1070
    class n1070 normalNode
    n1071[value]
    n1070 --> n1071
    class n1071 leafNode
    n1072[source]
    n1070 --> n1072
    class n1072 leafNode
    n1073[carbon]
    n1045 --> n1073
    class n1073 normalNode
    n1074[value]
    n1073 --> n1074
    class n1074 leafNode
    n1075[source]
    n1073 --> n1075
    class n1075 leafNode
    n1076[nitrogen]
    n1045 --> n1076
    class n1076 normalNode
    n1077[value]
    n1076 --> n1077
    class n1077 leafNode
    n1078[source]
    n1076 --> n1078
    class n1078 leafNode
    n1079[neon]
    n1045 --> n1079
    class n1079 normalNode
    n1080[value]
    n1079 --> n1080
    class n1080 leafNode
    n1081[source]
    n1079 --> n1081
    class n1081 leafNode
    n1082[argon]
    n1045 --> n1082
    class n1082 normalNode
    n1083[value]
    n1082 --> n1083
    class n1083 leafNode
    n1084[source]
    n1082 --> n1084
    class n1084 leafNode
    n1085[xenon]
    n1045 --> n1085
    class n1085 normalNode
    n1086[value]
    n1085 --> n1086
    class n1086 leafNode
    n1087[source]
    n1085 --> n1087
    class n1087 leafNode
    n1088[oxygen]
    n1045 --> n1088
    class n1088 normalNode
    n1089[value]
    n1088 --> n1089
    class n1089 leafNode
    n1090[source]
    n1088 --> n1090
    class n1090 leafNode
    n1091[tungsten]
    n1045 --> n1091
    class n1091 normalNode
    n1092[value]
    n1091 --> n1092
    class n1092 leafNode
    n1093[source]
    n1091 --> n1093
    class n1093 leafNode
    n1094[iron]
    n1045 --> n1094
    class n1094 normalNode
    n1095[value]
    n1094 --> n1095
    class n1095 leafNode
    n1096[source]
    n1094 --> n1096
    class n1096 leafNode
    n1097[krypton]
    n1045 --> n1097
    class n1097 normalNode
    n1098[value]
    n1097 --> n1098
    class n1098 leafNode
    n1099[source]
    n1097 --> n1099
    class n1099 leafNode
    n1100[n_i_total]
    n1032 --> n1100
    class n1100 normalNode
    n1101[value]
    n1100 --> n1101
    class n1101 leafNode
    n1102[source]
    n1100 --> n1102
    class n1102 leafNode
    n1103[zeff]
    n1032 --> n1103
    class n1103 normalNode
    n1104[value]
    n1103 --> n1104
    class n1104 leafNode
    n1105[source]
    n1103 --> n1105
    class n1105 leafNode
    n1106[flux_expansion]
    n1032 --> n1106
    class n1106 normalNode
    n1107[value]
    n1106 --> n1107
    class n1107 leafNode
    n1108[source]
    n1106 --> n1108
    class n1108 leafNode
    n1109[power_flux_peak]
    n1032 --> n1109
    class n1109 normalNode
    n1110[value]
    n1109 --> n1110
    class n1110 leafNode
    n1111[source]
    n1109 --> n1111
    class n1111 leafNode
    n1112[r_eff_norm_2_3]
    n248 --> n1112
    class n1112 normalNode
    n1113[effective_helical_ripple]
    n1112 --> n1113
    class n1113 normalNode
    n1114[value]
    n1113 --> n1114
    class n1114 leafNode
    n1115[source]
    n1113 --> n1115
    class n1115 leafNode
    n1116[plateau_factor]
    n1112 --> n1116
    class n1116 normalNode
    n1117[value]
    n1116 --> n1117
    class n1117 leafNode
    n1118[source]
    n1116 --> n1118
    class n1118 leafNode
    n1119[iota]
    n1112 --> n1119
    class n1119 normalNode
    n1120[value]
    n1119 --> n1120
    class n1120 leafNode
    n1121[source]
    n1119 --> n1121
    class n1121 leafNode
    n1122(boundary)
    n1 --> n1122
    class n1122 complexNode
    n1123[type]
    n1122 --> n1123
    class n1123 normalNode
    n1124[value]
    n1123 --> n1124
    class n1124 leafNode
    n1125[source]
    n1123 --> n1125
    class n1125 leafNode
    n1126[geometric_axis_r]
    n1122 --> n1126
    class n1126 normalNode
    n1127[value]
    n1126 --> n1127
    class n1127 leafNode
    n1128[source]
    n1126 --> n1128
    class n1128 leafNode
    n1129[geometric_axis_z]
    n1122 --> n1129
    class n1129 normalNode
    n1130[value]
    n1129 --> n1130
    class n1130 leafNode
    n1131[source]
    n1129 --> n1131
    class n1131 leafNode
    n1132[magnetic_axis_r]
    n1122 --> n1132
    class n1132 normalNode
    n1133[value]
    n1132 --> n1133
    class n1133 leafNode
    n1134[source]
    n1132 --> n1134
    class n1134 leafNode
    n1135[magnetic_axis_z]
    n1122 --> n1135
    class n1135 normalNode
    n1136[value]
    n1135 --> n1136
    class n1136 leafNode
    n1137[source]
    n1135 --> n1137
    class n1137 leafNode
    n1138[minor_radius]
    n1122 --> n1138
    class n1138 normalNode
    n1139[value]
    n1138 --> n1139
    class n1139 leafNode
    n1140[source]
    n1138 --> n1140
    class n1140 leafNode
    n1141[elongation]
    n1122 --> n1141
    class n1141 normalNode
    n1142[value]
    n1141 --> n1142
    class n1142 leafNode
    n1143[source]
    n1141 --> n1143
    class n1143 leafNode
    n1144[triangularity_upper]
    n1122 --> n1144
    class n1144 normalNode
    n1145[value]
    n1144 --> n1145
    class n1145 leafNode
    n1146[source]
    n1144 --> n1146
    class n1146 leafNode
    n1147[triangularity_lower]
    n1122 --> n1147
    class n1147 normalNode
    n1148[value]
    n1147 --> n1148
    class n1148 leafNode
    n1149[source]
    n1147 --> n1149
    class n1149 leafNode
    n1150[strike_point_inner_r]
    n1122 --> n1150
    class n1150 normalNode
    n1151[value]
    n1150 --> n1151
    class n1151 leafNode
    n1152[source]
    n1150 --> n1152
    class n1152 leafNode
    n1153[strike_point_inner_z]
    n1122 --> n1153
    class n1153 normalNode
    n1154[value]
    n1153 --> n1154
    class n1154 leafNode
    n1155[source]
    n1153 --> n1155
    class n1155 leafNode
    n1156[strike_point_outer_r]
    n1122 --> n1156
    class n1156 normalNode
    n1157[value]
    n1156 --> n1157
    class n1157 leafNode
    n1158[source]
    n1156 --> n1158
    class n1158 leafNode
    n1159[strike_point_outer_z]
    n1122 --> n1159
    class n1159 normalNode
    n1160[value]
    n1159 --> n1160
    class n1160 leafNode
    n1161[source]
    n1159 --> n1161
    class n1161 leafNode
    n1162[strike_point_configuration]
    n1122 --> n1162
    class n1162 normalNode
    n1163[value]
    n1162 --> n1163
    class n1163 leafNode
    n1164[source]
    n1162 --> n1164
    class n1164 leafNode
    n1165[gap_limiter_wall]
    n1122 --> n1165
    class n1165 normalNode
    n1166[value]
    n1165 --> n1166
    class n1166 leafNode
    n1167[source]
    n1165 --> n1167
    class n1167 leafNode
    n1168[distance_inner_outer_separatrices]
    n1122 --> n1168
    class n1168 normalNode
    n1169[value]
    n1168 --> n1169
    class n1169 leafNode
    n1170[source]
    n1168 --> n1170
    class n1170 leafNode
    n1171[x_point_main]
    n1122 --> n1171
    class n1171 normalNode
    n1172[r]
    n1171 --> n1172
    class n1172 leafNode
    n1173[z]
    n1171 --> n1173
    class n1173 leafNode
    n1174[source]
    n1171 --> n1174
    class n1174 leafNode
    n1175[pedestal_fits]
    n1 --> n1175
    class n1175 normalNode
    n1176(mtanh)
    n1175 --> n1176
    class n1176 complexNode
    n1177(n_e)
    n1176 --> n1177
    class n1177 complexNode
    n1178[separatrix]
    n1177 --> n1178
    class n1178 normalNode
    n1179[value]
    n1178 --> n1179
    class n1179 leafNode
    n1180[source]
    n1178 --> n1180
    class n1180 leafNode
    n1181[pedestal_height]
    n1177 --> n1181
    class n1181 normalNode
    n1182[value]
    n1181 --> n1182
    class n1182 leafNode
    n1183[source]
    n1181 --> n1183
    class n1183 leafNode
    n1184[pedestal_width]
    n1177 --> n1184
    class n1184 normalNode
    n1185[value]
    n1184 --> n1185
    class n1185 leafNode
    n1186[source]
    n1184 --> n1186
    class n1186 leafNode
    n1187[pedestal_position]
    n1177 --> n1187
    class n1187 normalNode
    n1188[value]
    n1187 --> n1188
    class n1188 leafNode
    n1189[source]
    n1187 --> n1189
    class n1189 leafNode
    n1190[offset]
    n1177 --> n1190
    class n1190 normalNode
    n1191[value]
    n1190 --> n1191
    class n1191 leafNode
    n1192[source]
    n1190 --> n1192
    class n1192 leafNode
    n1193[d_dpsi_norm]
    n1177 --> n1193
    class n1193 normalNode
    n1194[value]
    n1193 --> n1194
    class n1194 leafNode
    n1195[source]
    n1193 --> n1195
    class n1195 leafNode
    n1196[d_dpsi_norm_max]
    n1177 --> n1196
    class n1196 normalNode
    n1197[value]
    n1196 --> n1197
    class n1197 leafNode
    n1198[source]
    n1196 --> n1198
    class n1198 leafNode
    n1199[d_dpsi_norm_max_position]
    n1177 --> n1199
    class n1199 normalNode
    n1200[value]
    n1199 --> n1200
    class n1200 leafNode
    n1201[source]
    n1199 --> n1201
    class n1201 leafNode
    n1202(t_e)
    n1176 --> n1202
    class n1202 complexNode
    n1203[pedestal_height]
    n1202 --> n1203
    class n1203 normalNode
    n1204[value]
    n1203 --> n1204
    class n1204 leafNode
    n1205[source]
    n1203 --> n1205
    class n1205 leafNode
    n1206[pedestal_width]
    n1202 --> n1206
    class n1206 normalNode
    n1207[value]
    n1206 --> n1207
    class n1207 leafNode
    n1208[source]
    n1206 --> n1208
    class n1208 leafNode
    n1209[pedestal_position]
    n1202 --> n1209
    class n1209 normalNode
    n1210[value]
    n1209 --> n1210
    class n1210 leafNode
    n1211[source]
    n1209 --> n1211
    class n1211 leafNode
    n1212[offset]
    n1202 --> n1212
    class n1212 normalNode
    n1213[value]
    n1212 --> n1213
    class n1213 leafNode
    n1214[source]
    n1212 --> n1214
    class n1214 leafNode
    n1215[d_dpsi_norm]
    n1202 --> n1215
    class n1215 normalNode
    n1216[value]
    n1215 --> n1216
    class n1216 leafNode
    n1217[source]
    n1215 --> n1217
    class n1217 leafNode
    n1218[d_dpsi_norm_max]
    n1202 --> n1218
    class n1218 normalNode
    n1219[value]
    n1218 --> n1219
    class n1219 leafNode
    n1220[source]
    n1218 --> n1220
    class n1220 leafNode
    n1221[d_dpsi_norm_max_position]
    n1202 --> n1221
    class n1221 normalNode
    n1222[value]
    n1221 --> n1222
    class n1222 leafNode
    n1223[source]
    n1221 --> n1223
    class n1223 leafNode
    n1224(pressure_electron)
    n1176 --> n1224
    class n1224 complexNode
    n1225[separatrix]
    n1224 --> n1225
    class n1225 normalNode
    n1226[value]
    n1225 --> n1226
    class n1226 leafNode
    n1227[source]
    n1225 --> n1227
    class n1227 leafNode
    n1228[pedestal_height]
    n1224 --> n1228
    class n1228 normalNode
    n1229[value]
    n1228 --> n1229
    class n1229 leafNode
    n1230[source]
    n1228 --> n1230
    class n1230 leafNode
    n1231[pedestal_width]
    n1224 --> n1231
    class n1231 normalNode
    n1232[value]
    n1231 --> n1232
    class n1232 leafNode
    n1233[source]
    n1231 --> n1233
    class n1233 leafNode
    n1234[pedestal_position]
    n1224 --> n1234
    class n1234 normalNode
    n1235[value]
    n1234 --> n1235
    class n1235 leafNode
    n1236[source]
    n1234 --> n1236
    class n1236 leafNode
    n1237[offset]
    n1224 --> n1237
    class n1237 normalNode
    n1238[value]
    n1237 --> n1238
    class n1238 leafNode
    n1239[source]
    n1237 --> n1239
    class n1239 leafNode
    n1240[d_dpsi_norm]
    n1224 --> n1240
    class n1240 normalNode
    n1241[value]
    n1240 --> n1241
    class n1241 leafNode
    n1242[source]
    n1240 --> n1242
    class n1242 leafNode
    n1243[d_dpsi_norm_max]
    n1224 --> n1243
    class n1243 normalNode
    n1244[value]
    n1243 --> n1244
    class n1244 leafNode
    n1245[source]
    n1243 --> n1245
    class n1245 leafNode
    n1246[d_dpsi_norm_max_position]
    n1224 --> n1246
    class n1246 normalNode
    n1247[value]
    n1246 --> n1247
    class n1247 leafNode
    n1248[source]
    n1246 --> n1248
    class n1248 leafNode
    n1249[energy_thermal_pedestal_electron]
    n1176 --> n1249
    class n1249 normalNode
    n1250[value]
    n1249 --> n1250
    class n1250 leafNode
    n1251[source]
    n1249 --> n1251
    class n1251 leafNode
    n1252[energy_thermal_pedestal_ion]
    n1176 --> n1252
    class n1252 normalNode
    n1253[value]
    n1252 --> n1253
    class n1253 leafNode
    n1254[source]
    n1252 --> n1254
    class n1254 leafNode
    n1255[volume_inside_pedestal]
    n1176 --> n1255
    class n1255 normalNode
    n1256[value]
    n1255 --> n1256
    class n1256 leafNode
    n1257[source]
    n1255 --> n1257
    class n1257 leafNode
    n1258[alpha_electron_pedestal_max]
    n1176 --> n1258
    class n1258 normalNode
    n1259[value]
    n1258 --> n1259
    class n1259 leafNode
    n1260[source]
    n1258 --> n1260
    class n1260 leafNode
    n1261[alpha_electron_pedestal_max_position]
    n1176 --> n1261
    class n1261 normalNode
    n1262[value]
    n1261 --> n1262
    class n1262 leafNode
    n1263[source]
    n1261 --> n1263
    class n1263 leafNode
    n1264[beta_pol_pedestal_top_electron_average]
    n1176 --> n1264
    class n1264 normalNode
    n1265[value]
    n1264 --> n1265
    class n1265 leafNode
    n1266[source]
    n1264 --> n1266
    class n1266 leafNode
    n1267[beta_pol_pedestal_top_electron_lfs]
    n1176 --> n1267
    class n1267 normalNode
    n1268[value]
    n1267 --> n1268
    class n1268 leafNode
    n1269[source]
    n1267 --> n1269
    class n1269 leafNode
    n1270[beta_pol_pedestal_top_electron_hfs]
    n1176 --> n1270
    class n1270 normalNode
    n1271[value]
    n1270 --> n1271
    class n1271 leafNode
    n1272[source]
    n1270 --> n1272
    class n1272 leafNode
    n1273[nustar_pedestal_top_electron]
    n1176 --> n1273
    class n1273 normalNode
    n1274[value]
    n1273 --> n1274
    class n1274 leafNode
    n1275[source]
    n1273 --> n1275
    class n1275 leafNode
    n1276[rhostar_pedestal_top_electron_lfs]
    n1176 --> n1276
    class n1276 normalNode
    n1277[value]
    n1276 --> n1277
    class n1277 leafNode
    n1278[source]
    n1276 --> n1278
    class n1278 leafNode
    n1279[rhostar_pedestal_top_electron_hfs]
    n1176 --> n1279
    class n1279 normalNode
    n1280[value]
    n1279 --> n1280
    class n1280 leafNode
    n1281[source]
    n1279 --> n1281
    class n1281 leafNode
    n1282[rhostar_pedestal_top_electron_magnetic_axis]
    n1176 --> n1282
    class n1282 normalNode
    n1283[value]
    n1282 --> n1283
    class n1283 leafNode
    n1284[source]
    n1282 --> n1284
    class n1284 leafNode
    n1285[b_field_pol_pedestal_top_average]
    n1176 --> n1285
    class n1285 normalNode
    n1286[value]
    n1285 --> n1286
    class n1286 leafNode
    n1287[source]
    n1285 --> n1287
    class n1287 leafNode
    n1288[b_field_pol_pedestal_top_hfs]
    n1176 --> n1288
    class n1288 normalNode
    n1289[value]
    n1288 --> n1289
    class n1289 leafNode
    n1290[source]
    n1288 --> n1290
    class n1290 leafNode
    n1291[b_field_pol_pedestal_top_lfs]
    n1176 --> n1291
    class n1291 normalNode
    n1292[value]
    n1291 --> n1292
    class n1292 leafNode
    n1293[source]
    n1291 --> n1293
    class n1293 leafNode
    n1294[b_field_pedestal_top_hfs]
    n1176 --> n1294
    class n1294 normalNode
    n1295[value]
    n1294 --> n1295
    class n1295 leafNode
    n1296[source]
    n1294 --> n1296
    class n1296 leafNode
    n1297[b_field_pedestal_top_lfs]
    n1176 --> n1297
    class n1297 normalNode
    n1298[value]
    n1297 --> n1298
    class n1298 leafNode
    n1299[source]
    n1297 --> n1299
    class n1299 leafNode
    n1300[b_field_tor_pedestal_top_hfs]
    n1176 --> n1300
    class n1300 normalNode
    n1301[value]
    n1300 --> n1301
    class n1301 leafNode
    n1302[source]
    n1300 --> n1302
    class n1302 leafNode
    n1303[b_field_tor_pedestal_top_lfs]
    n1176 --> n1303
    class n1303 normalNode
    n1304[value]
    n1303 --> n1304
    class n1304 leafNode
    n1305[source]
    n1303 --> n1305
    class n1305 leafNode
    n1306[coulomb_factor_pedestal_top]
    n1176 --> n1306
    class n1306 normalNode
    n1307[value]
    n1306 --> n1307
    class n1307 leafNode
    n1308[source]
    n1306 --> n1308
    class n1308 leafNode
    n1309[stability]
    n1176 --> n1309
    class n1309 normalNode
    n1310[alpha_experimental]
    n1309 --> n1310
    class n1310 normalNode
    n1311[value]
    n1310 --> n1311
    class n1311 leafNode
    n1312[source]
    n1310 --> n1312
    class n1312 leafNode
    n1313[bootstrap_current_sauter]
    n1309 --> n1313
    class n1313 normalNode
    n1314[alpha_critical]
    n1313 --> n1314
    class n1314 normalNode
    n1315[value]
    n1314 --> n1315
    class n1315 leafNode
    n1316[source]
    n1314 --> n1316
    class n1316 leafNode
    n1317[alpha_ratio]
    n1313 --> n1317
    class n1317 normalNode
    n1318[value]
    n1317 --> n1318
    class n1318 leafNode
    n1319[source]
    n1317 --> n1319
    class n1319 leafNode
    n1320[t_e_pedestal_top_critical]
    n1313 --> n1320
    class n1320 normalNode
    n1321[value]
    n1320 --> n1321
    class n1321 leafNode
    n1322[source]
    n1320 --> n1322
    class n1322 leafNode
    n1323[bootstrap_current_hager]
    n1309 --> n1323
    class n1323 normalNode
    n1324[alpha_critical]
    n1323 --> n1324
    class n1324 normalNode
    n1325[value]
    n1324 --> n1325
    class n1325 leafNode
    n1326[source]
    n1324 --> n1326
    class n1326 leafNode
    n1327[alpha_ratio]
    n1323 --> n1327
    class n1327 normalNode
    n1328[value]
    n1327 --> n1328
    class n1328 leafNode
    n1329[source]
    n1327 --> n1329
    class n1329 leafNode
    n1330[t_e_pedestal_top_critical]
    n1323 --> n1330
    class n1330 normalNode
    n1331[value]
    n1330 --> n1331
    class n1331 leafNode
    n1332[source]
    n1330 --> n1332
    class n1332 leafNode
    n1333[parameters]
    n1176 --> n1333
    class n1333 leafNode
    n1334(linear)
    n1175 --> n1334
    class n1334 complexNode
    n1335(n_e)
    n1334 --> n1335
    class n1335 complexNode
    n1336[separatrix]
    n1335 --> n1336
    class n1336 normalNode
    n1337[value]
    n1336 --> n1337
    class n1337 leafNode
    n1338[source]
    n1336 --> n1338
    class n1338 leafNode
    n1339[pedestal_height]
    n1335 --> n1339
    class n1339 normalNode
    n1340[value]
    n1339 --> n1340
    class n1340 leafNode
    n1341[source]
    n1339 --> n1341
    class n1341 leafNode
    n1342[pedestal_width]
    n1335 --> n1342
    class n1342 normalNode
    n1343[value]
    n1342 --> n1343
    class n1343 leafNode
    n1344[source]
    n1342 --> n1344
    class n1344 leafNode
    n1345[pedestal_position]
    n1335 --> n1345
    class n1345 normalNode
    n1346[value]
    n1345 --> n1346
    class n1346 leafNode
    n1347[source]
    n1345 --> n1347
    class n1347 leafNode
    n1348[offset]
    n1335 --> n1348
    class n1348 normalNode
    n1349[value]
    n1348 --> n1349
    class n1349 leafNode
    n1350[source]
    n1348 --> n1350
    class n1350 leafNode
    n1351[d_dpsi_norm]
    n1335 --> n1351
    class n1351 normalNode
    n1352[value]
    n1351 --> n1352
    class n1352 leafNode
    n1353[source]
    n1351 --> n1353
    class n1353 leafNode
    n1354[d_dpsi_norm_max]
    n1335 --> n1354
    class n1354 normalNode
    n1355[value]
    n1354 --> n1355
    class n1355 leafNode
    n1356[source]
    n1354 --> n1356
    class n1356 leafNode
    n1357(t_e)
    n1334 --> n1357
    class n1357 complexNode
    n1358[pedestal_height]
    n1357 --> n1358
    class n1358 normalNode
    n1359[value]
    n1358 --> n1359
    class n1359 leafNode
    n1360[source]
    n1358 --> n1360
    class n1360 leafNode
    n1361[pedestal_width]
    n1357 --> n1361
    class n1361 normalNode
    n1362[value]
    n1361 --> n1362
    class n1362 leafNode
    n1363[source]
    n1361 --> n1363
    class n1363 leafNode
    n1364[pedestal_position]
    n1357 --> n1364
    class n1364 normalNode
    n1365[value]
    n1364 --> n1365
    class n1365 leafNode
    n1366[source]
    n1364 --> n1366
    class n1366 leafNode
    n1367[offset]
    n1357 --> n1367
    class n1367 normalNode
    n1368[value]
    n1367 --> n1368
    class n1368 leafNode
    n1369[source]
    n1367 --> n1369
    class n1369 leafNode
    n1370[d_dpsi_norm]
    n1357 --> n1370
    class n1370 normalNode
    n1371[value]
    n1370 --> n1371
    class n1371 leafNode
    n1372[source]
    n1370 --> n1372
    class n1372 leafNode
    n1373[d_dpsi_norm_max]
    n1357 --> n1373
    class n1373 normalNode
    n1374[value]
    n1373 --> n1374
    class n1374 leafNode
    n1375[source]
    n1373 --> n1375
    class n1375 leafNode
    n1376(pressure_electron)
    n1334 --> n1376
    class n1376 complexNode
    n1377[separatrix]
    n1376 --> n1377
    class n1377 normalNode
    n1378[value]
    n1377 --> n1378
    class n1378 leafNode
    n1379[source]
    n1377 --> n1379
    class n1379 leafNode
    n1380[pedestal_height]
    n1376 --> n1380
    class n1380 normalNode
    n1381[value]
    n1380 --> n1381
    class n1381 leafNode
    n1382[source]
    n1380 --> n1382
    class n1382 leafNode
    n1383[pedestal_width]
    n1376 --> n1383
    class n1383 normalNode
    n1384[value]
    n1383 --> n1384
    class n1384 leafNode
    n1385[source]
    n1383 --> n1385
    class n1385 leafNode
    n1386[pedestal_position]
    n1376 --> n1386
    class n1386 normalNode
    n1387[value]
    n1386 --> n1387
    class n1387 leafNode
    n1388[source]
    n1386 --> n1388
    class n1388 leafNode
    n1389[offset]
    n1376 --> n1389
    class n1389 normalNode
    n1390[value]
    n1389 --> n1390
    class n1390 leafNode
    n1391[source]
    n1389 --> n1391
    class n1391 leafNode
    n1392[d_dpsi_norm]
    n1376 --> n1392
    class n1392 normalNode
    n1393[value]
    n1392 --> n1393
    class n1393 leafNode
    n1394[source]
    n1392 --> n1394
    class n1394 leafNode
    n1395[d_dpsi_norm_max]
    n1376 --> n1395
    class n1395 normalNode
    n1396[value]
    n1395 --> n1396
    class n1396 leafNode
    n1397[source]
    n1395 --> n1397
    class n1397 leafNode
    n1398[d_dpsi_norm_max_position]
    n1376 --> n1398
    class n1398 normalNode
    n1399[value]
    n1398 --> n1399
    class n1399 leafNode
    n1400[source]
    n1398 --> n1400
    class n1400 leafNode
    n1401[energy_thermal_pedestal_electron]
    n1334 --> n1401
    class n1401 normalNode
    n1402[value]
    n1401 --> n1402
    class n1402 leafNode
    n1403[source]
    n1401 --> n1403
    class n1403 leafNode
    n1404[energy_thermal_pedestal_ion]
    n1334 --> n1404
    class n1404 normalNode
    n1405[value]
    n1404 --> n1405
    class n1405 leafNode
    n1406[source]
    n1404 --> n1406
    class n1406 leafNode
    n1407[volume_inside_pedestal]
    n1334 --> n1407
    class n1407 normalNode
    n1408[value]
    n1407 --> n1408
    class n1408 leafNode
    n1409[source]
    n1407 --> n1409
    class n1409 leafNode
    n1410[beta_pol_pedestal_top_electron_average]
    n1334 --> n1410
    class n1410 normalNode
    n1411[value]
    n1410 --> n1411
    class n1411 leafNode
    n1412[source]
    n1410 --> n1412
    class n1412 leafNode
    n1413[beta_pol_pedestal_top_electron_lfs]
    n1334 --> n1413
    class n1413 normalNode
    n1414[value]
    n1413 --> n1414
    class n1414 leafNode
    n1415[source]
    n1413 --> n1415
    class n1415 leafNode
    n1416[beta_pol_pedestal_top_electron_hfs]
    n1334 --> n1416
    class n1416 normalNode
    n1417[value]
    n1416 --> n1417
    class n1417 leafNode
    n1418[source]
    n1416 --> n1418
    class n1418 leafNode
    n1419[nustar_pedestal_top_electron]
    n1334 --> n1419
    class n1419 normalNode
    n1420[value]
    n1419 --> n1420
    class n1420 leafNode
    n1421[source]
    n1419 --> n1421
    class n1421 leafNode
    n1422[rhostar_pedestal_top_electron_lfs]
    n1334 --> n1422
    class n1422 normalNode
    n1423[value]
    n1422 --> n1423
    class n1423 leafNode
    n1424[source]
    n1422 --> n1424
    class n1424 leafNode
    n1425[rhostar_pedestal_top_electron_hfs]
    n1334 --> n1425
    class n1425 normalNode
    n1426[value]
    n1425 --> n1426
    class n1426 leafNode
    n1427[source]
    n1425 --> n1427
    class n1427 leafNode
    n1428[rhostar_pedestal_top_electron_magnetic_axis]
    n1334 --> n1428
    class n1428 normalNode
    n1429[value]
    n1428 --> n1429
    class n1429 leafNode
    n1430[source]
    n1428 --> n1430
    class n1430 leafNode
    n1431[b_field_pol_pedestal_top_average]
    n1334 --> n1431
    class n1431 normalNode
    n1432[value]
    n1431 --> n1432
    class n1432 leafNode
    n1433[source]
    n1431 --> n1433
    class n1433 leafNode
    n1434[b_field_pol_pedestal_top_hfs]
    n1334 --> n1434
    class n1434 normalNode
    n1435[value]
    n1434 --> n1435
    class n1435 leafNode
    n1436[source]
    n1434 --> n1436
    class n1436 leafNode
    n1437[b_field_pol_pedestal_top_lfs]
    n1334 --> n1437
    class n1437 normalNode
    n1438[value]
    n1437 --> n1438
    class n1438 leafNode
    n1439[source]
    n1437 --> n1439
    class n1439 leafNode
    n1440[b_field_pedestal_top_hfs]
    n1334 --> n1440
    class n1440 normalNode
    n1441[value]
    n1440 --> n1441
    class n1441 leafNode
    n1442[source]
    n1440 --> n1442
    class n1442 leafNode
    n1443[b_field_pedestal_top_lfs]
    n1334 --> n1443
    class n1443 normalNode
    n1444[value]
    n1443 --> n1444
    class n1444 leafNode
    n1445[source]
    n1443 --> n1445
    class n1445 leafNode
    n1446[b_field_tor_pedestal_top_hfs]
    n1334 --> n1446
    class n1446 normalNode
    n1447[value]
    n1446 --> n1447
    class n1447 leafNode
    n1448[source]
    n1446 --> n1448
    class n1448 leafNode
    n1449[b_field_tor_pedestal_top_lfs]
    n1334 --> n1449
    class n1449 normalNode
    n1450[value]
    n1449 --> n1450
    class n1450 leafNode
    n1451[source]
    n1449 --> n1451
    class n1451 leafNode
    n1452[coulomb_factor_pedestal_top]
    n1334 --> n1452
    class n1452 normalNode
    n1453[value]
    n1452 --> n1453
    class n1453 leafNode
    n1454[source]
    n1452 --> n1454
    class n1454 leafNode
    n1455[parameters]
    n1334 --> n1455
    class n1455 leafNode
    n1456(line_average)
    n1 --> n1456
    class n1456 complexNode
    n1457[t_e]
    n1456 --> n1457
    class n1457 normalNode
    n1458[value]
    n1457 --> n1458
    class n1458 leafNode
    n1459[source]
    n1457 --> n1459
    class n1459 leafNode
    n1460[t_i_average]
    n1456 --> n1460
    class n1460 normalNode
    n1461[value]
    n1460 --> n1461
    class n1461 leafNode
    n1462[source]
    n1460 --> n1462
    class n1462 leafNode
    n1463[n_e]
    n1456 --> n1463
    class n1463 normalNode
    n1464[value]
    n1463 --> n1464
    class n1464 leafNode
    n1465[source]
    n1463 --> n1465
    class n1465 leafNode
    n1466[dn_e_dt]
    n1456 --> n1466
    class n1466 normalNode
    n1467[value]
    n1466 --> n1467
    class n1467 leafNode
    n1468[source]
    n1466 --> n1468
    class n1468 leafNode
    n1469(n_i)
    n1456 --> n1469
    class n1469 complexNode
    n1470[hydrogen]
    n1469 --> n1470
    class n1470 normalNode
    n1471[value]
    n1470 --> n1471
    class n1471 leafNode
    n1472[source]
    n1470 --> n1472
    class n1472 leafNode
    n1473[deuterium]
    n1469 --> n1473
    class n1473 normalNode
    n1474[value]
    n1473 --> n1474
    class n1474 leafNode
    n1475[source]
    n1473 --> n1475
    class n1475 leafNode
    n1476[tritium]
    n1469 --> n1476
    class n1476 normalNode
    n1477[value]
    n1476 --> n1477
    class n1477 leafNode
    n1478[source]
    n1476 --> n1478
    class n1478 leafNode
    n1479[deuterium_tritium]
    n1469 --> n1479
    class n1479 normalNode
    n1480[value]
    n1479 --> n1480
    class n1480 leafNode
    n1481[source]
    n1479 --> n1481
    class n1481 leafNode
    n1482[helium_3]
    n1469 --> n1482
    class n1482 normalNode
    n1483[value]
    n1482 --> n1483
    class n1483 leafNode
    n1484[source]
    n1482 --> n1484
    class n1484 leafNode
    n1485[helium_4]
    n1469 --> n1485
    class n1485 normalNode
    n1486[value]
    n1485 --> n1486
    class n1486 leafNode
    n1487[source]
    n1485 --> n1487
    class n1487 leafNode
    n1488[beryllium]
    n1469 --> n1488
    class n1488 normalNode
    n1489[value]
    n1488 --> n1489
    class n1489 leafNode
    n1490[source]
    n1488 --> n1490
    class n1490 leafNode
    n1491[boron]
    n1469 --> n1491
    class n1491 normalNode
    n1492[value]
    n1491 --> n1492
    class n1492 leafNode
    n1493[source]
    n1491 --> n1493
    class n1493 leafNode
    n1494[lithium]
    n1469 --> n1494
    class n1494 normalNode
    n1495[value]
    n1494 --> n1495
    class n1495 leafNode
    n1496[source]
    n1494 --> n1496
    class n1496 leafNode
    n1497[carbon]
    n1469 --> n1497
    class n1497 normalNode
    n1498[value]
    n1497 --> n1498
    class n1498 leafNode
    n1499[source]
    n1497 --> n1499
    class n1499 leafNode
    n1500[nitrogen]
    n1469 --> n1500
    class n1500 normalNode
    n1501[value]
    n1500 --> n1501
    class n1501 leafNode
    n1502[source]
    n1500 --> n1502
    class n1502 leafNode
    n1503[neon]
    n1469 --> n1503
    class n1503 normalNode
    n1504[value]
    n1503 --> n1504
    class n1504 leafNode
    n1505[source]
    n1503 --> n1505
    class n1505 leafNode
    n1506[argon]
    n1469 --> n1506
    class n1506 normalNode
    n1507[value]
    n1506 --> n1507
    class n1507 leafNode
    n1508[source]
    n1506 --> n1508
    class n1508 leafNode
    n1509[xenon]
    n1469 --> n1509
    class n1509 normalNode
    n1510[value]
    n1509 --> n1510
    class n1510 leafNode
    n1511[source]
    n1509 --> n1511
    class n1511 leafNode
    n1512[oxygen]
    n1469 --> n1512
    class n1512 normalNode
    n1513[value]
    n1512 --> n1513
    class n1513 leafNode
    n1514[source]
    n1512 --> n1514
    class n1514 leafNode
    n1515[tungsten]
    n1469 --> n1515
    class n1515 normalNode
    n1516[value]
    n1515 --> n1516
    class n1516 leafNode
    n1517[source]
    n1515 --> n1517
    class n1517 leafNode
    n1518[iron]
    n1469 --> n1518
    class n1518 normalNode
    n1519[value]
    n1518 --> n1519
    class n1519 leafNode
    n1520[source]
    n1518 --> n1520
    class n1520 leafNode
    n1521[krypton]
    n1469 --> n1521
    class n1521 normalNode
    n1522[value]
    n1521 --> n1522
    class n1522 leafNode
    n1523[source]
    n1521 --> n1523
    class n1523 leafNode
    n1524[n_i_total]
    n1456 --> n1524
    class n1524 normalNode
    n1525[value]
    n1524 --> n1525
    class n1525 leafNode
    n1526[source]
    n1524 --> n1526
    class n1526 leafNode
    n1527[zeff]
    n1456 --> n1527
    class n1527 normalNode
    n1528[value]
    n1527 --> n1528
    class n1528 leafNode
    n1529[source]
    n1527 --> n1529
    class n1529 leafNode
    n1530[meff_hydrogenic]
    n1456 --> n1530
    class n1530 normalNode
    n1531[value]
    n1530 --> n1531
    class n1531 leafNode
    n1532[source]
    n1530 --> n1532
    class n1532 leafNode
    n1533[isotope_fraction_hydrogen]
    n1456 --> n1533
    class n1533 normalNode
    n1534[value]
    n1533 --> n1534
    class n1534 leafNode
    n1535[source]
    n1533 --> n1535
    class n1535 leafNode
    n1536(volume_average)
    n1 --> n1536
    class n1536 complexNode
    n1537[t_e]
    n1536 --> n1537
    class n1537 normalNode
    n1538[value]
    n1537 --> n1538
    class n1538 leafNode
    n1539[source]
    n1537 --> n1539
    class n1539 leafNode
    n1540[t_i_average]
    n1536 --> n1540
    class n1540 normalNode
    n1541[value]
    n1540 --> n1541
    class n1541 leafNode
    n1542[source]
    n1540 --> n1542
    class n1542 leafNode
    n1543[n_e]
    n1536 --> n1543
    class n1543 normalNode
    n1544[value]
    n1543 --> n1544
    class n1544 leafNode
    n1545[source]
    n1543 --> n1545
    class n1545 leafNode
    n1546[dn_e_dt]
    n1536 --> n1546
    class n1546 normalNode
    n1547[value]
    n1546 --> n1547
    class n1547 leafNode
    n1548[source]
    n1546 --> n1548
    class n1548 leafNode
    n1549(n_i)
    n1536 --> n1549
    class n1549 complexNode
    n1550[hydrogen]
    n1549 --> n1550
    class n1550 normalNode
    n1551[value]
    n1550 --> n1551
    class n1551 leafNode
    n1552[source]
    n1550 --> n1552
    class n1552 leafNode
    n1553[deuterium]
    n1549 --> n1553
    class n1553 normalNode
    n1554[value]
    n1553 --> n1554
    class n1554 leafNode
    n1555[source]
    n1553 --> n1555
    class n1555 leafNode
    n1556[tritium]
    n1549 --> n1556
    class n1556 normalNode
    n1557[value]
    n1556 --> n1557
    class n1557 leafNode
    n1558[source]
    n1556 --> n1558
    class n1558 leafNode
    n1559[deuterium_tritium]
    n1549 --> n1559
    class n1559 normalNode
    n1560[value]
    n1559 --> n1560
    class n1560 leafNode
    n1561[source]
    n1559 --> n1561
    class n1561 leafNode
    n1562[helium_3]
    n1549 --> n1562
    class n1562 normalNode
    n1563[value]
    n1562 --> n1563
    class n1563 leafNode
    n1564[source]
    n1562 --> n1564
    class n1564 leafNode
    n1565[helium_4]
    n1549 --> n1565
    class n1565 normalNode
    n1566[value]
    n1565 --> n1566
    class n1566 leafNode
    n1567[source]
    n1565 --> n1567
    class n1567 leafNode
    n1568[beryllium]
    n1549 --> n1568
    class n1568 normalNode
    n1569[value]
    n1568 --> n1569
    class n1569 leafNode
    n1570[source]
    n1568 --> n1570
    class n1570 leafNode
    n1571[boron]
    n1549 --> n1571
    class n1571 normalNode
    n1572[value]
    n1571 --> n1572
    class n1572 leafNode
    n1573[source]
    n1571 --> n1573
    class n1573 leafNode
    n1574[lithium]
    n1549 --> n1574
    class n1574 normalNode
    n1575[value]
    n1574 --> n1575
    class n1575 leafNode
    n1576[source]
    n1574 --> n1576
    class n1576 leafNode
    n1577[carbon]
    n1549 --> n1577
    class n1577 normalNode
    n1578[value]
    n1577 --> n1578
    class n1578 leafNode
    n1579[source]
    n1577 --> n1579
    class n1579 leafNode
    n1580[nitrogen]
    n1549 --> n1580
    class n1580 normalNode
    n1581[value]
    n1580 --> n1581
    class n1581 leafNode
    n1582[source]
    n1580 --> n1582
    class n1582 leafNode
    n1583[neon]
    n1549 --> n1583
    class n1583 normalNode
    n1584[value]
    n1583 --> n1584
    class n1584 leafNode
    n1585[source]
    n1583 --> n1585
    class n1585 leafNode
    n1586[argon]
    n1549 --> n1586
    class n1586 normalNode
    n1587[value]
    n1586 --> n1587
    class n1587 leafNode
    n1588[source]
    n1586 --> n1588
    class n1588 leafNode
    n1589[xenon]
    n1549 --> n1589
    class n1589 normalNode
    n1590[value]
    n1589 --> n1590
    class n1590 leafNode
    n1591[source]
    n1589 --> n1591
    class n1591 leafNode
    n1592[oxygen]
    n1549 --> n1592
    class n1592 normalNode
    n1593[value]
    n1592 --> n1593
    class n1593 leafNode
    n1594[source]
    n1592 --> n1594
    class n1594 leafNode
    n1595[tungsten]
    n1549 --> n1595
    class n1595 normalNode
    n1596[value]
    n1595 --> n1596
    class n1596 leafNode
    n1597[source]
    n1595 --> n1597
    class n1597 leafNode
    n1598[iron]
    n1549 --> n1598
    class n1598 normalNode
    n1599[value]
    n1598 --> n1599
    class n1599 leafNode
    n1600[source]
    n1598 --> n1600
    class n1600 leafNode
    n1601[krypton]
    n1549 --> n1601
    class n1601 normalNode
    n1602[value]
    n1601 --> n1602
    class n1602 leafNode
    n1603[source]
    n1601 --> n1603
    class n1603 leafNode
    n1604[n_i_total]
    n1536 --> n1604
    class n1604 normalNode
    n1605[value]
    n1604 --> n1605
    class n1605 leafNode
    n1606[source]
    n1604 --> n1606
    class n1606 leafNode
    n1607[zeff]
    n1536 --> n1607
    class n1607 normalNode
    n1608[value]
    n1607 --> n1608
    class n1608 leafNode
    n1609[source]
    n1607 --> n1609
    class n1609 leafNode
    n1610[meff_hydrogenic]
    n1536 --> n1610
    class n1610 normalNode
    n1611[value]
    n1610 --> n1611
    class n1611 leafNode
    n1612[source]
    n1610 --> n1612
    class n1612 leafNode
    n1613[isotope_fraction_hydrogen]
    n1536 --> n1613
    class n1613 normalNode
    n1614[value]
    n1613 --> n1614
    class n1614 leafNode
    n1615[source]
    n1613 --> n1615
    class n1615 leafNode
    n1616(disruption)
    n1 --> n1616
    class n1616 complexNode
    n1617[time]
    n1616 --> n1617
    class n1617 normalNode
    n1618[value]
    n1617 --> n1618
    class n1618 leafNode
    n1619[source]
    n1617 --> n1619
    class n1619 leafNode
    n1620[time_radiated_power_max]
    n1616 --> n1620
    class n1620 normalNode
    n1621[value]
    n1620 --> n1621
    class n1621 leafNode
    n1622[source]
    n1620 --> n1622
    class n1622 leafNode
    n1623[time_half_ip]
    n1616 --> n1623
    class n1623 normalNode
    n1624[value]
    n1623 --> n1624
    class n1624 leafNode
    n1625[source]
    n1623 --> n1625
    class n1625 leafNode
    n1626[vertical_displacement]
    n1616 --> n1626
    class n1626 normalNode
    n1627[value]
    n1626 --> n1627
    class n1627 leafNode
    n1628[source]
    n1626 --> n1628
    class n1628 leafNode
    n1629[mitigation_valve]
    n1616 --> n1629
    class n1629 normalNode
    n1630[value]
    n1629 --> n1630
    class n1630 leafNode
    n1631[source]
    n1629 --> n1631
    class n1631 leafNode
    n1632[decay_times]
    n1616 --> n1632
    class n1632 normalNode
    n1633[ip]
    n1632 --> n1633
    class n1633 normalNode
    n1634[linear_20_80]
    n1633 --> n1634
    class n1634 normalNode
    n1635[value]
    n1634 --> n1635
    class n1635 leafNode
    n1636[source]
    n1634 --> n1636
    class n1636 leafNode
    n1637[linear_custom]
    n1633 --> n1637
    class n1637 normalNode
    n1638[x1]
    n1637 --> n1638
    class n1638 leafNode
    n1639[x2]
    n1637 --> n1639
    class n1639 leafNode
    n1640[decay_time]
    n1637 --> n1640
    class n1640 normalNode
    n1641[value]
    n1640 --> n1641
    class n1641 leafNode
    n1642[source]
    n1640 --> n1642
    class n1642 leafNode
    n1643[exponential]
    n1633 --> n1643
    class n1643 normalNode
    n1644[value]
    n1643 --> n1644
    class n1644 leafNode
    n1645[source]
    n1643 --> n1645
    class n1645 leafNode
    n1646[current_runaways]
    n1632 --> n1646
    class n1646 normalNode
    n1647[linear_20_80]
    n1646 --> n1647
    class n1647 normalNode
    n1648[value]
    n1647 --> n1648
    class n1648 leafNode
    n1649[source]
    n1647 --> n1649
    class n1649 leafNode
    n1650[linear_custom]
    n1646 --> n1650
    class n1650 normalNode
    n1651[x1]
    n1650 --> n1651
    class n1651 leafNode
    n1652[x2]
    n1650 --> n1652
    class n1652 leafNode
    n1653[decay_time]
    n1650 --> n1653
    class n1653 normalNode
    n1654[value]
    n1653 --> n1654
    class n1654 leafNode
    n1655[source]
    n1653 --> n1655
    class n1655 leafNode
    n1656[exponential]
    n1646 --> n1656
    class n1656 normalNode
    n1657[value]
    n1656 --> n1657
    class n1657 leafNode
    n1658[source]
    n1656 --> n1658
    class n1658 leafNode
    n1659[t_e_volume_average]
    n1632 --> n1659
    class n1659 normalNode
    n1660[linear_20_80]
    n1659 --> n1660
    class n1660 normalNode
    n1661[value]
    n1660 --> n1661
    class n1661 leafNode
    n1662[source]
    n1660 --> n1662
    class n1662 leafNode
    n1663[linear_custom]
    n1659 --> n1663
    class n1663 normalNode
    n1664[x1]
    n1663 --> n1664
    class n1664 leafNode
    n1665[x2]
    n1663 --> n1665
    class n1665 leafNode
    n1666[decay_time]
    n1663 --> n1666
    class n1666 normalNode
    n1667[value]
    n1666 --> n1667
    class n1667 leafNode
    n1668[source]
    n1666 --> n1668
    class n1668 leafNode
    n1669[exponential]
    n1659 --> n1669
    class n1669 normalNode
    n1670[value]
    n1669 --> n1670
    class n1670 leafNode
    n1671[source]
    n1669 --> n1671
    class n1671 leafNode
    n1672[t_e_magnetic_axis]
    n1632 --> n1672
    class n1672 normalNode
    n1673[linear_20_80]
    n1672 --> n1673
    class n1673 normalNode
    n1674[value]
    n1673 --> n1674
    class n1674 leafNode
    n1675[source]
    n1673 --> n1675
    class n1675 leafNode
    n1676[linear_custom]
    n1672 --> n1676
    class n1676 normalNode
    n1677[x1]
    n1676 --> n1677
    class n1677 leafNode
    n1678[x2]
    n1676 --> n1678
    class n1678 leafNode
    n1679[decay_time]
    n1676 --> n1679
    class n1679 normalNode
    n1680[value]
    n1679 --> n1680
    class n1680 leafNode
    n1681[source]
    n1679 --> n1681
    class n1681 leafNode
    n1682[exponential]
    n1672 --> n1682
    class n1682 normalNode
    n1683[value]
    n1682 --> n1683
    class n1683 leafNode
    n1684[source]
    n1682 --> n1684
    class n1684 leafNode
    n1685[energy_thermal]
    n1632 --> n1685
    class n1685 normalNode
    n1686[linear_20_80]
    n1685 --> n1686
    class n1686 normalNode
    n1687[value]
    n1686 --> n1687
    class n1687 leafNode
    n1688[source]
    n1686 --> n1688
    class n1688 leafNode
    n1689[linear_custom]
    n1685 --> n1689
    class n1689 normalNode
    n1690[x1]
    n1689 --> n1690
    class n1690 leafNode
    n1691[x2]
    n1689 --> n1691
    class n1691 leafNode
    n1692[decay_time]
    n1689 --> n1692
    class n1692 normalNode
    n1693[value]
    n1692 --> n1693
    class n1693 leafNode
    n1694[source]
    n1692 --> n1694
    class n1694 leafNode
    n1695[exponential]
    n1685 --> n1695
    class n1695 normalNode
    n1696[value]
    n1695 --> n1696
    class n1696 leafNode
    n1697[source]
    n1695 --> n1697
    class n1697 leafNode
    n1698[elms]
    n1 --> n1698
    class n1698 normalNode
    n1699[frequency]
    n1698 --> n1699
    class n1699 normalNode
    n1700[value]
    n1699 --> n1700
    class n1700 leafNode
    n1701[source]
    n1699 --> n1701
    class n1701 leafNode
    n1702[type]
    n1698 --> n1702
    class n1702 normalNode
    n1703[value]
    n1702 --> n1703
    class n1703 leafNode
    n1704[source]
    n1702 --> n1704
    class n1704 leafNode
    n1705[fusion]
    n1 --> n1705
    class n1705 normalNode
    n1706[power]
    n1705 --> n1706
    class n1706 normalNode
    n1707[value]
    n1706 --> n1707
    class n1707 leafNode
    n1708[source]
    n1706 --> n1708
    class n1708 leafNode
    n1709[current]
    n1705 --> n1709
    class n1709 normalNode
    n1710[value]
    n1709 --> n1710
    class n1710 leafNode
    n1711[source]
    n1709 --> n1711
    class n1711 leafNode
    n1712[neutron_rates]
    n1705 --> n1712
    class n1712 normalNode
    n1713[total]
    n1712 --> n1713
    class n1713 normalNode
    n1714[value]
    n1713 --> n1714
    class n1714 leafNode
    n1715[source]
    n1713 --> n1715
    class n1715 leafNode
    n1716[thermal]
    n1712 --> n1716
    class n1716 normalNode
    n1717[value]
    n1716 --> n1717
    class n1717 leafNode
    n1718[source]
    n1716 --> n1718
    class n1718 leafNode
    n1719[dd]
    n1712 --> n1719
    class n1719 normalNode
    n1720[total]
    n1719 --> n1720
    class n1720 normalNode
    n1721[value]
    n1720 --> n1721
    class n1721 leafNode
    n1722[source]
    n1720 --> n1722
    class n1722 leafNode
    n1723[thermal]
    n1719 --> n1723
    class n1723 normalNode
    n1724[value]
    n1723 --> n1724
    class n1724 leafNode
    n1725[source]
    n1723 --> n1725
    class n1725 leafNode
    n1726[beam_thermal]
    n1719 --> n1726
    class n1726 normalNode
    n1727[value]
    n1726 --> n1727
    class n1727 leafNode
    n1728[source]
    n1726 --> n1728
    class n1728 leafNode
    n1729[beam_beam]
    n1719 --> n1729
    class n1729 normalNode
    n1730[value]
    n1729 --> n1730
    class n1730 leafNode
    n1731[source]
    n1729 --> n1731
    class n1731 leafNode
    n1732[dt]
    n1712 --> n1732
    class n1732 normalNode
    n1733[total]
    n1732 --> n1733
    class n1733 normalNode
    n1734[value]
    n1733 --> n1734
    class n1734 leafNode
    n1735[source]
    n1733 --> n1735
    class n1735 leafNode
    n1736[thermal]
    n1732 --> n1736
    class n1736 normalNode
    n1737[value]
    n1736 --> n1737
    class n1737 leafNode
    n1738[source]
    n1736 --> n1738
    class n1738 leafNode
    n1739[beam_thermal]
    n1732 --> n1739
    class n1739 normalNode
    n1740[value]
    n1739 --> n1740
    class n1740 leafNode
    n1741[source]
    n1739 --> n1741
    class n1741 leafNode
    n1742[beam_beam]
    n1732 --> n1742
    class n1742 normalNode
    n1743[value]
    n1742 --> n1743
    class n1743 leafNode
    n1744[source]
    n1742 --> n1744
    class n1744 leafNode
    n1745[tt]
    n1712 --> n1745
    class n1745 normalNode
    n1746[total]
    n1745 --> n1746
    class n1746 normalNode
    n1747[value]
    n1746 --> n1747
    class n1747 leafNode
    n1748[source]
    n1746 --> n1748
    class n1748 leafNode
    n1749[thermal]
    n1745 --> n1749
    class n1749 normalNode
    n1750[value]
    n1749 --> n1750
    class n1750 leafNode
    n1751[source]
    n1749 --> n1751
    class n1751 leafNode
    n1752[beam_thermal]
    n1745 --> n1752
    class n1752 normalNode
    n1753[value]
    n1752 --> n1753
    class n1753 leafNode
    n1754[source]
    n1752 --> n1754
    class n1754 leafNode
    n1755[beam_beam]
    n1745 --> n1755
    class n1755 normalNode
    n1756[value]
    n1755 --> n1756
    class n1756 leafNode
    n1757[source]
    n1755 --> n1757
    class n1757 leafNode
    n1758[neutron_power_total]
    n1705 --> n1758
    class n1758 normalNode
    n1759[value]
    n1758 --> n1759
    class n1759 leafNode
    n1760[source]
    n1758 --> n1760
    class n1760 leafNode
    n1761(gas_injection_rates)
    n1 --> n1761
    class n1761 complexNode
    n1762[total]
    n1761 --> n1762
    class n1762 normalNode
    n1763[value]
    n1762 --> n1763
    class n1763 leafNode
    n1764[source]
    n1762 --> n1764
    class n1764 leafNode
    n1765[midplane]
    n1761 --> n1765
    class n1765 normalNode
    n1766[value]
    n1765 --> n1766
    class n1766 leafNode
    n1767[source]
    n1765 --> n1767
    class n1767 leafNode
    n1768[top]
    n1761 --> n1768
    class n1768 normalNode
    n1769[value]
    n1768 --> n1769
    class n1769 leafNode
    n1770[source]
    n1768 --> n1770
    class n1770 leafNode
    n1771[bottom]
    n1761 --> n1771
    class n1771 normalNode
    n1772[value]
    n1771 --> n1772
    class n1772 leafNode
    n1773[source]
    n1771 --> n1773
    class n1773 leafNode
    n1774[hydrogen]
    n1761 --> n1774
    class n1774 normalNode
    n1775[value]
    n1774 --> n1775
    class n1775 leafNode
    n1776[source]
    n1774 --> n1776
    class n1776 leafNode
    n1777[deuterium]
    n1761 --> n1777
    class n1777 normalNode
    n1778[value]
    n1777 --> n1778
    class n1778 leafNode
    n1779[source]
    n1777 --> n1779
    class n1779 leafNode
    n1780[tritium]
    n1761 --> n1780
    class n1780 normalNode
    n1781[value]
    n1780 --> n1781
    class n1781 leafNode
    n1782[source]
    n1780 --> n1782
    class n1782 leafNode
    n1783[helium_3]
    n1761 --> n1783
    class n1783 normalNode
    n1784[value]
    n1783 --> n1784
    class n1784 leafNode
    n1785[source]
    n1783 --> n1785
    class n1785 leafNode
    n1786[helium_4]
    n1761 --> n1786
    class n1786 normalNode
    n1787[value]
    n1786 --> n1787
    class n1787 leafNode
    n1788[source]
    n1786 --> n1788
    class n1788 leafNode
    n1789[impurity_seeding]
    n1761 --> n1789
    class n1789 normalNode
    n1790[value]
    n1789 --> n1790
    class n1790 leafNode
    n1791[source]
    n1789 --> n1791
    class n1791 leafNode
    n1792[beryllium]
    n1761 --> n1792
    class n1792 normalNode
    n1793[value]
    n1792 --> n1793
    class n1793 leafNode
    n1794[source]
    n1792 --> n1794
    class n1794 leafNode
    n1795[lithium]
    n1761 --> n1795
    class n1795 normalNode
    n1796[value]
    n1795 --> n1796
    class n1796 leafNode
    n1797[source]
    n1795 --> n1797
    class n1797 leafNode
    n1798[carbon]
    n1761 --> n1798
    class n1798 normalNode
    n1799[value]
    n1798 --> n1799
    class n1799 leafNode
    n1800[source]
    n1798 --> n1800
    class n1800 leafNode
    n1801[oxygen]
    n1761 --> n1801
    class n1801 normalNode
    n1802[value]
    n1801 --> n1802
    class n1802 leafNode
    n1803[source]
    n1801 --> n1803
    class n1803 leafNode
    n1804[nitrogen]
    n1761 --> n1804
    class n1804 normalNode
    n1805[value]
    n1804 --> n1805
    class n1805 leafNode
    n1806[source]
    n1804 --> n1806
    class n1806 leafNode
    n1807[neon]
    n1761 --> n1807
    class n1807 normalNode
    n1808[value]
    n1807 --> n1808
    class n1808 leafNode
    n1809[source]
    n1807 --> n1809
    class n1809 leafNode
    n1810[argon]
    n1761 --> n1810
    class n1810 normalNode
    n1811[value]
    n1810 --> n1811
    class n1811 leafNode
    n1812[source]
    n1810 --> n1812
    class n1812 leafNode
    n1813[xenon]
    n1761 --> n1813
    class n1813 normalNode
    n1814[value]
    n1813 --> n1814
    class n1814 leafNode
    n1815[source]
    n1813 --> n1815
    class n1815 leafNode
    n1816[krypton]
    n1761 --> n1816
    class n1816 normalNode
    n1817[value]
    n1816 --> n1817
    class n1817 leafNode
    n1818[source]
    n1816 --> n1818
    class n1818 leafNode
    n1819[methane]
    n1761 --> n1819
    class n1819 normalNode
    n1820[value]
    n1819 --> n1820
    class n1820 leafNode
    n1821[source]
    n1819 --> n1821
    class n1821 leafNode
    n1822[methane_carbon_13]
    n1761 --> n1822
    class n1822 normalNode
    n1823[value]
    n1822 --> n1823
    class n1823 leafNode
    n1824[source]
    n1822 --> n1824
    class n1824 leafNode
    n1825[methane_deuterated]
    n1761 --> n1825
    class n1825 normalNode
    n1826[value]
    n1825 --> n1826
    class n1826 leafNode
    n1827[source]
    n1825 --> n1827
    class n1827 leafNode
    n1828[silane]
    n1761 --> n1828
    class n1828 normalNode
    n1829[value]
    n1828 --> n1829
    class n1829 leafNode
    n1830[source]
    n1828 --> n1830
    class n1830 leafNode
    n1831[ethylene]
    n1761 --> n1831
    class n1831 normalNode
    n1832[value]
    n1831 --> n1832
    class n1832 leafNode
    n1833[source]
    n1831 --> n1833
    class n1833 leafNode
    n1834[ethane]
    n1761 --> n1834
    class n1834 normalNode
    n1835[value]
    n1834 --> n1835
    class n1835 leafNode
    n1836[source]
    n1834 --> n1836
    class n1836 leafNode
    n1837[propane]
    n1761 --> n1837
    class n1837 normalNode
    n1838[value]
    n1837 --> n1838
    class n1838 leafNode
    n1839[source]
    n1837 --> n1839
    class n1839 leafNode
    n1840[ammonia]
    n1761 --> n1840
    class n1840 normalNode
    n1841[value]
    n1840 --> n1841
    class n1841 leafNode
    n1842[source]
    n1840 --> n1842
    class n1842 leafNode
    n1843[ammonia_deuterated]
    n1761 --> n1843
    class n1843 normalNode
    n1844[value]
    n1843 --> n1844
    class n1844 leafNode
    n1845[source]
    n1843 --> n1845
    class n1845 leafNode
    n1846(gas_injection_accumulated)
    n1 --> n1846
    class n1846 complexNode
    n1847[total]
    n1846 --> n1847
    class n1847 normalNode
    n1848[value]
    n1847 --> n1848
    class n1848 leafNode
    n1849[source]
    n1847 --> n1849
    class n1849 leafNode
    n1850[midplane]
    n1846 --> n1850
    class n1850 normalNode
    n1851[value]
    n1850 --> n1851
    class n1851 leafNode
    n1852[source]
    n1850 --> n1852
    class n1852 leafNode
    n1853[top]
    n1846 --> n1853
    class n1853 normalNode
    n1854[value]
    n1853 --> n1854
    class n1854 leafNode
    n1855[source]
    n1853 --> n1855
    class n1855 leafNode
    n1856[bottom]
    n1846 --> n1856
    class n1856 normalNode
    n1857[value]
    n1856 --> n1857
    class n1857 leafNode
    n1858[source]
    n1856 --> n1858
    class n1858 leafNode
    n1859[hydrogen]
    n1846 --> n1859
    class n1859 normalNode
    n1860[value]
    n1859 --> n1860
    class n1860 leafNode
    n1861[source]
    n1859 --> n1861
    class n1861 leafNode
    n1862[deuterium]
    n1846 --> n1862
    class n1862 normalNode
    n1863[value]
    n1862 --> n1863
    class n1863 leafNode
    n1864[source]
    n1862 --> n1864
    class n1864 leafNode
    n1865[tritium]
    n1846 --> n1865
    class n1865 normalNode
    n1866[value]
    n1865 --> n1866
    class n1866 leafNode
    n1867[source]
    n1865 --> n1867
    class n1867 leafNode
    n1868[helium_3]
    n1846 --> n1868
    class n1868 normalNode
    n1869[value]
    n1868 --> n1869
    class n1869 leafNode
    n1870[source]
    n1868 --> n1870
    class n1870 leafNode
    n1871[helium_4]
    n1846 --> n1871
    class n1871 normalNode
    n1872[value]
    n1871 --> n1872
    class n1872 leafNode
    n1873[source]
    n1871 --> n1873
    class n1873 leafNode
    n1874[impurity_seeding]
    n1846 --> n1874
    class n1874 normalNode
    n1875[value]
    n1874 --> n1875
    class n1875 leafNode
    n1876[source]
    n1874 --> n1876
    class n1876 leafNode
    n1877[beryllium]
    n1846 --> n1877
    class n1877 normalNode
    n1878[value]
    n1877 --> n1878
    class n1878 leafNode
    n1879[source]
    n1877 --> n1879
    class n1879 leafNode
    n1880[lithium]
    n1846 --> n1880
    class n1880 normalNode
    n1881[value]
    n1880 --> n1881
    class n1881 leafNode
    n1882[source]
    n1880 --> n1882
    class n1882 leafNode
    n1883[carbon]
    n1846 --> n1883
    class n1883 normalNode
    n1884[value]
    n1883 --> n1884
    class n1884 leafNode
    n1885[source]
    n1883 --> n1885
    class n1885 leafNode
    n1886[oxygen]
    n1846 --> n1886
    class n1886 normalNode
    n1887[value]
    n1886 --> n1887
    class n1887 leafNode
    n1888[source]
    n1886 --> n1888
    class n1888 leafNode
    n1889[nitrogen]
    n1846 --> n1889
    class n1889 normalNode
    n1890[value]
    n1889 --> n1890
    class n1890 leafNode
    n1891[source]
    n1889 --> n1891
    class n1891 leafNode
    n1892[neon]
    n1846 --> n1892
    class n1892 normalNode
    n1893[value]
    n1892 --> n1893
    class n1893 leafNode
    n1894[source]
    n1892 --> n1894
    class n1894 leafNode
    n1895[argon]
    n1846 --> n1895
    class n1895 normalNode
    n1896[value]
    n1895 --> n1896
    class n1896 leafNode
    n1897[source]
    n1895 --> n1897
    class n1897 leafNode
    n1898[xenon]
    n1846 --> n1898
    class n1898 normalNode
    n1899[value]
    n1898 --> n1899
    class n1899 leafNode
    n1900[source]
    n1898 --> n1900
    class n1900 leafNode
    n1901[krypton]
    n1846 --> n1901
    class n1901 normalNode
    n1902[value]
    n1901 --> n1902
    class n1902 leafNode
    n1903[source]
    n1901 --> n1903
    class n1903 leafNode
    n1904[methane]
    n1846 --> n1904
    class n1904 normalNode
    n1905[value]
    n1904 --> n1905
    class n1905 leafNode
    n1906[source]
    n1904 --> n1906
    class n1906 leafNode
    n1907[methane_carbon_13]
    n1846 --> n1907
    class n1907 normalNode
    n1908[value]
    n1907 --> n1908
    class n1908 leafNode
    n1909[source]
    n1907 --> n1909
    class n1909 leafNode
    n1910[methane_deuterated]
    n1846 --> n1910
    class n1910 normalNode
    n1911[value]
    n1910 --> n1911
    class n1911 leafNode
    n1912[source]
    n1910 --> n1912
    class n1912 leafNode
    n1913[silane]
    n1846 --> n1913
    class n1913 normalNode
    n1914[value]
    n1913 --> n1914
    class n1914 leafNode
    n1915[source]
    n1913 --> n1915
    class n1915 leafNode
    n1916[ethylene]
    n1846 --> n1916
    class n1916 normalNode
    n1917[value]
    n1916 --> n1917
    class n1917 leafNode
    n1918[source]
    n1916 --> n1918
    class n1918 leafNode
    n1919[ethane]
    n1846 --> n1919
    class n1919 normalNode
    n1920[value]
    n1919 --> n1920
    class n1920 leafNode
    n1921[source]
    n1919 --> n1921
    class n1921 leafNode
    n1922[propane]
    n1846 --> n1922
    class n1922 normalNode
    n1923[value]
    n1922 --> n1923
    class n1923 leafNode
    n1924[source]
    n1922 --> n1924
    class n1924 leafNode
    n1925[ammonia]
    n1846 --> n1925
    class n1925 normalNode
    n1926[value]
    n1925 --> n1926
    class n1926 leafNode
    n1927[source]
    n1925 --> n1927
    class n1927 leafNode
    n1928[ammonia_deuterated]
    n1846 --> n1928
    class n1928 normalNode
    n1929[value]
    n1928 --> n1929
    class n1929 leafNode
    n1930[source]
    n1928 --> n1930
    class n1930 leafNode
    n1931(gas_injection_prefill)
    n1 --> n1931
    class n1931 complexNode
    n1932[total]
    n1931 --> n1932
    class n1932 normalNode
    n1933[value]
    n1932 --> n1933
    class n1933 leafNode
    n1934[source]
    n1932 --> n1934
    class n1934 leafNode
    n1935[midplane]
    n1931 --> n1935
    class n1935 normalNode
    n1936[value]
    n1935 --> n1936
    class n1936 leafNode
    n1937[source]
    n1935 --> n1937
    class n1937 leafNode
    n1938[top]
    n1931 --> n1938
    class n1938 normalNode
    n1939[value]
    n1938 --> n1939
    class n1939 leafNode
    n1940[source]
    n1938 --> n1940
    class n1940 leafNode
    n1941[bottom]
    n1931 --> n1941
    class n1941 normalNode
    n1942[value]
    n1941 --> n1942
    class n1942 leafNode
    n1943[source]
    n1941 --> n1943
    class n1943 leafNode
    n1944[hydrogen]
    n1931 --> n1944
    class n1944 normalNode
    n1945[value]
    n1944 --> n1945
    class n1945 leafNode
    n1946[source]
    n1944 --> n1946
    class n1946 leafNode
    n1947[deuterium]
    n1931 --> n1947
    class n1947 normalNode
    n1948[value]
    n1947 --> n1948
    class n1948 leafNode
    n1949[source]
    n1947 --> n1949
    class n1949 leafNode
    n1950[tritium]
    n1931 --> n1950
    class n1950 normalNode
    n1951[value]
    n1950 --> n1951
    class n1951 leafNode
    n1952[source]
    n1950 --> n1952
    class n1952 leafNode
    n1953[helium_3]
    n1931 --> n1953
    class n1953 normalNode
    n1954[value]
    n1953 --> n1954
    class n1954 leafNode
    n1955[source]
    n1953 --> n1955
    class n1955 leafNode
    n1956[helium_4]
    n1931 --> n1956
    class n1956 normalNode
    n1957[value]
    n1956 --> n1957
    class n1957 leafNode
    n1958[source]
    n1956 --> n1958
    class n1958 leafNode
    n1959[impurity_seeding]
    n1931 --> n1959
    class n1959 normalNode
    n1960[value]
    n1959 --> n1960
    class n1960 leafNode
    n1961[source]
    n1959 --> n1961
    class n1961 leafNode
    n1962[beryllium]
    n1931 --> n1962
    class n1962 normalNode
    n1963[value]
    n1962 --> n1963
    class n1963 leafNode
    n1964[source]
    n1962 --> n1964
    class n1964 leafNode
    n1965[lithium]
    n1931 --> n1965
    class n1965 normalNode
    n1966[value]
    n1965 --> n1966
    class n1966 leafNode
    n1967[source]
    n1965 --> n1967
    class n1967 leafNode
    n1968[carbon]
    n1931 --> n1968
    class n1968 normalNode
    n1969[value]
    n1968 --> n1969
    class n1969 leafNode
    n1970[source]
    n1968 --> n1970
    class n1970 leafNode
    n1971[oxygen]
    n1931 --> n1971
    class n1971 normalNode
    n1972[value]
    n1971 --> n1972
    class n1972 leafNode
    n1973[source]
    n1971 --> n1973
    class n1973 leafNode
    n1974[nitrogen]
    n1931 --> n1974
    class n1974 normalNode
    n1975[value]
    n1974 --> n1975
    class n1975 leafNode
    n1976[source]
    n1974 --> n1976
    class n1976 leafNode
    n1977[neon]
    n1931 --> n1977
    class n1977 normalNode
    n1978[value]
    n1977 --> n1978
    class n1978 leafNode
    n1979[source]
    n1977 --> n1979
    class n1979 leafNode
    n1980[argon]
    n1931 --> n1980
    class n1980 normalNode
    n1981[value]
    n1980 --> n1981
    class n1981 leafNode
    n1982[source]
    n1980 --> n1982
    class n1982 leafNode
    n1983[xenon]
    n1931 --> n1983
    class n1983 normalNode
    n1984[value]
    n1983 --> n1984
    class n1984 leafNode
    n1985[source]
    n1983 --> n1985
    class n1985 leafNode
    n1986[krypton]
    n1931 --> n1986
    class n1986 normalNode
    n1987[value]
    n1986 --> n1987
    class n1987 leafNode
    n1988[source]
    n1986 --> n1988
    class n1988 leafNode
    n1989[methane]
    n1931 --> n1989
    class n1989 normalNode
    n1990[value]
    n1989 --> n1990
    class n1990 leafNode
    n1991[source]
    n1989 --> n1991
    class n1991 leafNode
    n1992[methane_carbon_13]
    n1931 --> n1992
    class n1992 normalNode
    n1993[value]
    n1992 --> n1993
    class n1993 leafNode
    n1994[source]
    n1992 --> n1994
    class n1994 leafNode
    n1995[methane_deuterated]
    n1931 --> n1995
    class n1995 normalNode
    n1996[value]
    n1995 --> n1996
    class n1996 leafNode
    n1997[source]
    n1995 --> n1997
    class n1997 leafNode
    n1998[silane]
    n1931 --> n1998
    class n1998 normalNode
    n1999[value]
    n1998 --> n1999
    class n1999 leafNode
    n2000[source]
    n1998 --> n2000
    class n2000 leafNode
    n2001[ethylene]
    n1931 --> n2001
    class n2001 normalNode
    n2002[value]
    n2001 --> n2002
    class n2002 leafNode
    n2003[source]
    n2001 --> n2003
    class n2003 leafNode
    n2004[ethane]
    n1931 --> n2004
    class n2004 normalNode
    n2005[value]
    n2004 --> n2005
    class n2005 leafNode
    n2006[source]
    n2004 --> n2006
    class n2006 leafNode
    n2007[propane]
    n1931 --> n2007
    class n2007 normalNode
    n2008[value]
    n2007 --> n2008
    class n2008 leafNode
    n2009[source]
    n2007 --> n2009
    class n2009 leafNode
    n2010[ammonia]
    n1931 --> n2010
    class n2010 normalNode
    n2011[value]
    n2010 --> n2011
    class n2011 leafNode
    n2012[source]
    n2010 --> n2012
    class n2012 leafNode
    n2013[ammonia_deuterated]
    n1931 --> n2013
    class n2013 normalNode
    n2014[value]
    n2013 --> n2014
    class n2014 leafNode
    n2015[source]
    n2013 --> n2015
    class n2015 leafNode
    n2016(heating_current_drive)
    n1 --> n2016
    class n2016 complexNode
    n2017(ec)
    n2016 --> n2017
    class n2017 complexNode
    n2018[frequency]
    n2017 --> n2018
    class n2018 normalNode
    n2019[value]
    n2018 --> n2019
    class n2019 leafNode
    n2020[source]
    n2018 --> n2020
    class n2020 leafNode
    n2021[position]
    n2017 --> n2021
    class n2021 normalNode
    n2022[value]
    n2021 --> n2022
    class n2022 leafNode
    n2023[source]
    n2021 --> n2023
    class n2023 leafNode
    n2024[polarization]
    n2017 --> n2024
    class n2024 normalNode
    n2025[value]
    n2024 --> n2025
    class n2025 leafNode
    n2026[source]
    n2024 --> n2026
    class n2026 leafNode
    n2027[harmonic]
    n2017 --> n2027
    class n2027 normalNode
    n2028[value]
    n2027 --> n2028
    class n2028 leafNode
    n2029[source]
    n2027 --> n2029
    class n2029 leafNode
    n2030[phi]
    n2017 --> n2030
    class n2030 normalNode
    n2031[value]
    n2030 --> n2031
    class n2031 leafNode
    n2032[source]
    n2030 --> n2032
    class n2032 leafNode
    n2033[angle_pol]
    n2017 --> n2033
    class n2033 normalNode
    n2034[value]
    n2033 --> n2034
    class n2034 leafNode
    n2035[source]
    n2033 --> n2035
    class n2035 leafNode
    n2036[power]
    n2017 --> n2036
    class n2036 normalNode
    n2037[value]
    n2036 --> n2037
    class n2037 leafNode
    n2038[source]
    n2036 --> n2038
    class n2038 leafNode
    n2039[power_launched]
    n2017 --> n2039
    class n2039 normalNode
    n2040[value]
    n2039 --> n2040
    class n2040 leafNode
    n2041[source]
    n2039 --> n2041
    class n2041 leafNode
    n2042[current]
    n2017 --> n2042
    class n2042 normalNode
    n2043[value]
    n2042 --> n2043
    class n2043 leafNode
    n2044[source]
    n2042 --> n2044
    class n2044 leafNode
    n2045[energy_fast]
    n2017 --> n2045
    class n2045 normalNode
    n2046[value]
    n2045 --> n2046
    class n2046 leafNode
    n2047[source]
    n2045 --> n2047
    class n2047 leafNode
    n2048(nbi)
    n2016 --> n2048
    class n2048 complexNode
    n2049[species]
    n2048 --> n2049
    class n2049 normalNode
    n2050[a]
    n2049 --> n2050
    class n2050 normalNode
    n2051[value]
    n2050 --> n2051
    class n2051 leafNode
    n2052[source]
    n2050 --> n2052
    class n2052 leafNode
    n2053[z_n]
    n2049 --> n2053
    class n2053 normalNode
    n2054[value]
    n2053 --> n2054
    class n2054 leafNode
    n2055[source]
    n2053 --> n2055
    class n2055 leafNode
    n2056[name]
    n2049 --> n2056
    class n2056 normalNode
    n2057[value]
    n2056 --> n2057
    class n2057 leafNode
    n2058[source]
    n2056 --> n2058
    class n2058 leafNode
    n2059[power]
    n2048 --> n2059
    class n2059 normalNode
    n2060[value]
    n2059 --> n2060
    class n2060 leafNode
    n2061[source]
    n2059 --> n2061
    class n2061 leafNode
    n2062[power_launched]
    n2048 --> n2062
    class n2062 normalNode
    n2063[value]
    n2062 --> n2063
    class n2063 leafNode
    n2064[source]
    n2062 --> n2064
    class n2064 leafNode
    n2065[current]
    n2048 --> n2065
    class n2065 normalNode
    n2066[value]
    n2065 --> n2066
    class n2066 leafNode
    n2067[source]
    n2065 --> n2067
    class n2067 leafNode
    n2068[position]
    n2048 --> n2068
    class n2068 normalNode
    n2069[r]
    n2068 --> n2069
    class n2069 normalNode
    n2070[value]
    n2069 --> n2070
    class n2070 leafNode
    n2071[source]
    n2069 --> n2071
    class n2071 leafNode
    n2072[z]
    n2068 --> n2072
    class n2072 normalNode
    n2073[value]
    n2072 --> n2073
    class n2073 leafNode
    n2074[source]
    n2072 --> n2074
    class n2074 leafNode
    n2075[phi]
    n2068 --> n2075
    class n2075 normalNode
    n2076[value]
    n2075 --> n2076
    class n2076 leafNode
    n2077[source]
    n2075 --> n2077
    class n2077 leafNode
    n2078[tangency_radius]
    n2048 --> n2078
    class n2078 normalNode
    n2079[value]
    n2078 --> n2079
    class n2079 leafNode
    n2080[source]
    n2078 --> n2080
    class n2080 leafNode
    n2081[angle]
    n2048 --> n2081
    class n2081 normalNode
    n2082[value]
    n2081 --> n2082
    class n2082 leafNode
    n2083[source]
    n2081 --> n2083
    class n2083 leafNode
    n2084[direction]
    n2048 --> n2084
    class n2084 normalNode
    n2085[value]
    n2084 --> n2085
    class n2085 leafNode
    n2086[source]
    n2084 --> n2086
    class n2086 leafNode
    n2087[energy]
    n2048 --> n2087
    class n2087 normalNode
    n2088[value]
    n2087 --> n2088
    class n2088 leafNode
    n2089[source]
    n2087 --> n2089
    class n2089 leafNode
    n2090[beam_current_fraction]
    n2048 --> n2090
    class n2090 normalNode
    n2091[value]
    n2090 --> n2091
    class n2091 leafNode
    n2092[source]
    n2090 --> n2092
    class n2092 leafNode
    n2093[beam_power_fraction]
    n2048 --> n2093
    class n2093 normalNode
    n2094[value]
    n2093 --> n2094
    class n2094 leafNode
    n2095[source]
    n2093 --> n2095
    class n2095 leafNode
    n2096(ic)
    n2016 --> n2096
    class n2096 complexNode
    n2097[frequency]
    n2096 --> n2097
    class n2097 normalNode
    n2098[value]
    n2097 --> n2098
    class n2098 leafNode
    n2099[source]
    n2097 --> n2099
    class n2099 leafNode
    n2100[position]
    n2096 --> n2100
    class n2100 normalNode
    n2101[value]
    n2100 --> n2101
    class n2101 leafNode
    n2102[source]
    n2100 --> n2102
    class n2102 leafNode
    n2103[n_phi]
    n2096 --> n2103
    class n2103 normalNode
    n2104[value]
    n2103 --> n2104
    class n2104 leafNode
    n2105[source]
    n2103 --> n2105
    class n2105 leafNode
    n2106[k_perpendicular]
    n2096 --> n2106
    class n2106 normalNode
    n2107[value]
    n2106 --> n2107
    class n2107 leafNode
    n2108[source]
    n2106 --> n2108
    class n2108 leafNode
    n2109[e_field_plus_minus_ratio]
    n2096 --> n2109
    class n2109 normalNode
    n2110[value]
    n2109 --> n2110
    class n2110 leafNode
    n2111[source]
    n2109 --> n2111
    class n2111 leafNode
    n2112[harmonic]
    n2096 --> n2112
    class n2112 normalNode
    n2113[value]
    n2112 --> n2113
    class n2113 leafNode
    n2114[source]
    n2112 --> n2114
    class n2114 leafNode
    n2115[phase]
    n2096 --> n2115
    class n2115 normalNode
    n2116[value]
    n2115 --> n2116
    class n2116 leafNode
    n2117[source]
    n2115 --> n2117
    class n2117 leafNode
    n2118[power]
    n2096 --> n2118
    class n2118 normalNode
    n2119[value]
    n2118 --> n2119
    class n2119 leafNode
    n2120[source]
    n2118 --> n2120
    class n2120 leafNode
    n2121[power_launched]
    n2096 --> n2121
    class n2121 normalNode
    n2122[value]
    n2121 --> n2122
    class n2122 leafNode
    n2123[source]
    n2121 --> n2123
    class n2123 leafNode
    n2124[current]
    n2096 --> n2124
    class n2124 normalNode
    n2125[value]
    n2124 --> n2125
    class n2125 leafNode
    n2126[source]
    n2124 --> n2126
    class n2126 leafNode
    n2127[energy_fast]
    n2096 --> n2127
    class n2127 normalNode
    n2128[value]
    n2127 --> n2128
    class n2128 leafNode
    n2129[source]
    n2127 --> n2129
    class n2129 leafNode
    n2130(lh)
    n2016 --> n2130
    class n2130 complexNode
    n2131[frequency]
    n2130 --> n2131
    class n2131 normalNode
    n2132[value]
    n2131 --> n2132
    class n2132 leafNode
    n2133[source]
    n2131 --> n2133
    class n2133 leafNode
    n2134[position]
    n2130 --> n2134
    class n2134 normalNode
    n2135[value]
    n2134 --> n2135
    class n2135 leafNode
    n2136[source]
    n2134 --> n2136
    class n2136 leafNode
    n2137[n_parallel]
    n2130 --> n2137
    class n2137 normalNode
    n2138[value]
    n2137 --> n2138
    class n2138 leafNode
    n2139[source]
    n2137 --> n2139
    class n2139 leafNode
    n2140[power]
    n2130 --> n2140
    class n2140 normalNode
    n2141[value]
    n2140 --> n2141
    class n2141 leafNode
    n2142[source]
    n2140 --> n2142
    class n2142 leafNode
    n2143[power_launched]
    n2130 --> n2143
    class n2143 normalNode
    n2144[value]
    n2143 --> n2144
    class n2144 leafNode
    n2145[source]
    n2143 --> n2145
    class n2145 leafNode
    n2146[current]
    n2130 --> n2146
    class n2146 normalNode
    n2147[value]
    n2146 --> n2147
    class n2147 leafNode
    n2148[source]
    n2146 --> n2148
    class n2148 leafNode
    n2149[energy_fast]
    n2130 --> n2149
    class n2149 normalNode
    n2150[value]
    n2149 --> n2150
    class n2150 leafNode
    n2151[source]
    n2149 --> n2151
    class n2151 leafNode
    n2152[power_ec]
    n2016 --> n2152
    class n2152 normalNode
    n2153[value]
    n2152 --> n2153
    class n2153 leafNode
    n2154[source]
    n2152 --> n2154
    class n2154 leafNode
    n2155[power_launched_ec]
    n2016 --> n2155
    class n2155 normalNode
    n2156[value]
    n2155 --> n2156
    class n2156 leafNode
    n2157[source]
    n2155 --> n2157
    class n2157 leafNode
    n2158[power_nbi]
    n2016 --> n2158
    class n2158 normalNode
    n2159[value]
    n2158 --> n2159
    class n2159 leafNode
    n2160[source]
    n2158 --> n2160
    class n2160 leafNode
    n2161[power_launched_nbi]
    n2016 --> n2161
    class n2161 normalNode
    n2162[value]
    n2161 --> n2162
    class n2162 leafNode
    n2163[source]
    n2161 --> n2163
    class n2163 leafNode
    n2164[power_launched_nbi_co_injected_ratio]
    n2016 --> n2164
    class n2164 normalNode
    n2165[value]
    n2164 --> n2165
    class n2165 leafNode
    n2166[source]
    n2164 --> n2166
    class n2166 leafNode
    n2167[power_ic]
    n2016 --> n2167
    class n2167 normalNode
    n2168[value]
    n2167 --> n2168
    class n2168 leafNode
    n2169[source]
    n2167 --> n2169
    class n2169 leafNode
    n2170[power_launched_ic]
    n2016 --> n2170
    class n2170 normalNode
    n2171[value]
    n2170 --> n2171
    class n2171 leafNode
    n2172[source]
    n2170 --> n2172
    class n2172 leafNode
    n2173[power_lh]
    n2016 --> n2173
    class n2173 normalNode
    n2174[value]
    n2173 --> n2174
    class n2174 leafNode
    n2175[source]
    n2173 --> n2175
    class n2175 leafNode
    n2176[power_launched_lh]
    n2016 --> n2176
    class n2176 normalNode
    n2177[value]
    n2176 --> n2177
    class n2177 leafNode
    n2178[source]
    n2176 --> n2178
    class n2178 leafNode
    n2179[power_additional]
    n2016 --> n2179
    class n2179 normalNode
    n2180[value]
    n2179 --> n2180
    class n2180 leafNode
    n2181[source]
    n2179 --> n2181
    class n2181 leafNode
    n2182[kicks]
    n1 --> n2182
    class n2182 normalNode
    n2183[occurrence]
    n2182 --> n2183
    class n2183 normalNode
    n2184[value]
    n2183 --> n2184
    class n2184 leafNode
    n2185[source]
    n2183 --> n2185
    class n2185 leafNode
    n2186[pellets]
    n1 --> n2186
    class n2186 normalNode
    n2187[occurrence]
    n2186 --> n2187
    class n2187 normalNode
    n2188[value]
    n2187 --> n2188
    class n2188 leafNode
    n2189[source]
    n2187 --> n2189
    class n2189 leafNode
    n2190[rmps]
    n1 --> n2190
    class n2190 normalNode
    n2191[occurrence]
    n2190 --> n2191
    class n2191 normalNode
    n2192[value]
    n2191 --> n2192
    class n2192 leafNode
    n2193[source]
    n2191 --> n2193
    class n2193 leafNode
    n2194[runaways]
    n1 --> n2194
    class n2194 normalNode
    n2195[particles]
    n2194 --> n2195
    class n2195 normalNode
    n2196[value]
    n2195 --> n2196
    class n2196 leafNode
    n2197[source]
    n2195 --> n2197
    class n2197 leafNode
    n2198[current]
    n2194 --> n2198
    class n2198 normalNode
    n2199[value]
    n2198 --> n2199
    class n2199 leafNode
    n2200[source]
    n2198 --> n2200
    class n2200 leafNode
    n2201(scrape_off_layer)
    n1 --> n2201
    class n2201 complexNode
    n2202[t_e_decay_length]
    n2201 --> n2202
    class n2202 normalNode
    n2203[value]
    n2202 --> n2203
    class n2203 leafNode
    n2204[source]
    n2202 --> n2204
    class n2204 leafNode
    n2205[t_i_average_decay_length]
    n2201 --> n2205
    class n2205 normalNode
    n2206[value]
    n2205 --> n2206
    class n2206 leafNode
    n2207[source]
    n2205 --> n2207
    class n2207 leafNode
    n2208[n_e_decay_length]
    n2201 --> n2208
    class n2208 normalNode
    n2209[value]
    n2208 --> n2209
    class n2209 leafNode
    n2210[source]
    n2208 --> n2210
    class n2210 leafNode
    n2211[n_i_total_decay_length]
    n2201 --> n2211
    class n2211 normalNode
    n2212[value]
    n2211 --> n2212
    class n2212 leafNode
    n2213[source]
    n2211 --> n2213
    class n2213 leafNode
    n2214[heat_flux_e_decay_length]
    n2201 --> n2214
    class n2214 normalNode
    n2215[value]
    n2214 --> n2215
    class n2215 leafNode
    n2216[source]
    n2214 --> n2216
    class n2216 leafNode
    n2217[heat_flux_i_decay_length]
    n2201 --> n2217
    class n2217 normalNode
    n2218[value]
    n2217 --> n2218
    class n2218 leafNode
    n2219[source]
    n2217 --> n2219
    class n2219 leafNode
    n2220[power_radiated]
    n2201 --> n2220
    class n2220 normalNode
    n2221[value]
    n2220 --> n2221
    class n2221 leafNode
    n2222[source]
    n2220 --> n2222
    class n2222 leafNode
    n2223[pressure_neutral]
    n2201 --> n2223
    class n2223 normalNode
    n2224[value]
    n2223 --> n2224
    class n2224 leafNode
    n2225[source]
    n2223 --> n2225
    class n2225 leafNode
    n2226[wall]
    n1 --> n2226
    class n2226 normalNode
    n2227[material]
    n2226 --> n2227
    class n2227 normalNode
    n2228[name]
    n2227 --> n2228
    class n2228 leafNode
    n2229[index]
    n2227 --> n2229
    class n2229 leafNode
    n2230[description]
    n2227 --> n2230
    class n2230 leafNode
    n2231[evaporation]
    n2226 --> n2231
    class n2231 normalNode
    n2232[value]
    n2231 --> n2232
    class n2232 leafNode
    n2233[source]
    n2231 --> n2233
    class n2233 leafNode
    n2234[limiter]
    n1 --> n2234
    class n2234 normalNode
    n2235[material]
    n2234 --> n2235
    class n2235 normalNode
    n2236[name]
    n2235 --> n2236
    class n2236 leafNode
    n2237[index]
    n2235 --> n2237
    class n2237 leafNode
    n2238[description]
    n2235 --> n2238
    class n2238 leafNode
    n2239[time_breakdown]
    n1 --> n2239
    class n2239 normalNode
    n2240[value]
    n2239 --> n2240
    class n2240 leafNode
    n2241[source]
    n2239 --> n2241
    class n2241 leafNode
    n2242[plasma_duration]
    n1 --> n2242
    class n2242 normalNode
    n2243[value]
    n2242 --> n2243
    class n2243 leafNode
    n2244[source]
    n2242 --> n2244
    class n2244 leafNode
    n2245[time_width]
    n1 --> n2245
    class n2245 leafNode
    n2246[time]
    n1 --> n2246
    class n2246 leafNode

    classDef leafNode fill:#e1f5fe
    classDef complexNode fill:#fff3e0
    classDef normalNode fill:#f3e5f5
    classDef moreNode fill:#f5f5f5,stroke-dasharray: 5 5
```