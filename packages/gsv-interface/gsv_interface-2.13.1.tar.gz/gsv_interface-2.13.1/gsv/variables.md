# Summary of Phase 2 Reduced portfolio

## Accepted variables for Reduced Portfolio

### Sfc variables

|       Short Name     | GRIB ParamId |  Levtype | Hourly             | Monthly            |
| -------------------- | ------------ | -------- | ------------------ | ------------------ |
| tcwl                 | 78           |  sfc     | :white_check_mark: | :x:                |
| tciw                 | 79           |  sfc     | :white_check_mark: | :x:                |
| sp                   | 134          |  sfc     | :white_check_mark: | :x:                |
| msl                  | 151          |  sfc     | :white_check_mark: | :white_check_mark: |
| 10u                  | 165          |  sfc     | :white_check_mark: | :x:                |
| 10v                  | 166          |  sfc     | :white_check_mark: | :x:                |
| 2t                   | 167          |  sfc     | :white_check_mark: | :x:                |
| 2d                   | 168          |  sfc     | :white_check_mark: | :x:                |
| 10si                 | 207          |  sfc     | :white_check_mark: | :x:                |
| skt                  | 235          |  sfc     | :white_check_mark: | :x:                |
| avg_2t               | 228004       |  sfc     | :x:                | :white_check_mark: |
| tcc                  | 228164       |  sfc     | :white_check_mark: | :x:                |
| avg_tsrwe            | 235031       |  sfc     | :x:                | :white_check_mark: |
| avg_ishf             | 235033       |  sfc     | :white_check_mark: | :white_check_mark: |
| avg_slhtf            | 235034       |  sfc     | :white_check_mark: | :white_check_mark: |
| avg_sdswrf           | 235035       |  sfc     | :x:                | :white_check_mark: |
| avg_sdlwrf           | 235036       |  sfc     | :x:                | :white_check_mark: |
| avg_snswrf           | 235037       |  sfc     | :white_check_mark: | :white_check_mark: |
| avg_snlwrf           | 235038       |  sfc     | :white_check_mark: | :white_check_mark: |
| avg_tnswrf           | 235039       |  sfc     | :white_check_mark: | :white_check_mark: |
| avg_tnlwrf           | 235040       |  sfc     | :white_check_mark: | :white_check_mark: |
| avg_iews             | 235041       |  sfc     | :x:                | :white_check_mark: |
| avg_inss             | 235042       |  sfc     | :x:                | :white_check_mark: |
| avg_ie               | 235043       |  sfc     | :x:                | :white_check_mark: |
| avg_tnswrfcs         | 235049       |  sfc     | :x:                | :white_check_mark: |
| avg_tnlwrfcs         | 235050       |  sfc     | :x:                | :white_check_mark: |
| avg_snswrfcs         | 235051       |  sfc     | :x:                | :white_check_mark: |
| avg_snlwrfcs         | 235052       |  sfc     | :x:                | :white_check_mark: |
| avg_tdswrf           | 235053       |  sfc     | :x:                | :white_check_mark: |
| avg_tprate           | 235055       |  sfc     | :x:                | :white_check_mark: |
| avg_tnlwrfcs         | 235050       |  sfc     | :x:                | :white_check_mark: |
| avg_msl              | 235151       |  sfc     | :x:                | :white_check_mark: |
| avg_10u              | 235165       |  sfc     | :x:                | :white_check_mark: |
| avg_10v              | 235166       |  sfc     | :x:                | :white_check_mark: |
| avg_tcc              | 235288       |  sfc     | :x:                | :white_check_mark: |

### sfc daily (constant) variables

|       Short Name     | GRIB ParamId |  Levtype | Daily              | Monthly            |
| -------------------- | ------------ | -------- | ------------------ | ------------------ |
| lsm                  | 172          |  sfc     | :white_check_mark: | :x:                |
| orog                 | 228002       |  sfc     | :white_check_mark: | :x:                |

### pl variables

|       Short Name     | GRIB ParamId |  Levtype | Hourly             |  Monthly           |
| -------------------- | ------------ | -------- | ------------------ | ------------------ |
| z                    | 129          |  pl      | :white_check_mark: | :x:                |
| t                    | 130          |  pl      | :white_check_mark: | :white_check_mark: |
| u                    | 131          |  pl      | :white_check_mark: | :white_check_mark: |
| v                    | 132          |  pl      | :white_check_mark: | :white_check_mark: |
| q                    | 133          |  pl      | :white_check_mark: | :white_check_mark: |
| w                    | 135          |  pl      | :white_check_mark: | :x:                |

### o2d variables

|       Short Name     | GRIB ParamId |  Levtype | Daily              | Monthly            |
| -------------------- | ------------ | -------- | ------------------ | ------------------ |
| avg_sithick          | 263000       |  o2d     | :white_check_mark: | :white_check_mark: |
| avg_siconc           | 263001       |  o2d     | :white_check_mark: | :white_check_mark: |
| avg_sivol            | 263008       |  o2d     | :x:                | :white_check_mark: |
| avg_sos              | 263100       |  o2d     | :white_check_mark: | :white_check_mark: |
| avg_tos              | 263101       |  o2d     | :white_check_mark: | :white_check_mark: |
| avg_hc300m           | 263121       |  o2d     | :x:                | :white_check_mark: |
| avg_hc700m           | 263122       |  o2d     | :x:                | :white_check_mark: |
| avg_zos              | 263124       |  o2d     | :white_check_mark: | :x:                |

### o3d variables
|       Short Name     | GRIB ParamId |  Levtype | Daily              | Monthly            |
| -------------------- | ------------ | -------- | ------------------ | ------------------ |
| avg_so               | 263500       |  o3d     | :x:                | :white_check_mark: |
| avg_thetao           | 263501       |  o3d     | :x:                | :white_check_mark: |

### hl variables

|       Short Name     | GRIB ParamId |  Levtype | Hourly             | Monthly            |
| -------------------- | ------------ | -------- | ------------------ | ------------------ |
| u                    | 131          |  hl      | :white_check_mark: |                    |
| v                    | 132          |  hl      | :white_check_mark: |                    |