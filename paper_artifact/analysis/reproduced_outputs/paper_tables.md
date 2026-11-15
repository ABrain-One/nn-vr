# Reproduced paper tables

Derived only from packaged retained evidence. No new experiment.

## compatibility

| population | n | a_success | b_success | a_rate_percent | b_rate_percent | net_gain | change_pp | pp | fp | pf | ff | mcnemar_p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| p1 | 1762 | 1067 | 1177 | 60.55618615 | 66.79909194 | 110 | 6.242905789 | 1061 | 116 | 6 | 579 | 1.601865981e-27 |
| p2 | 1186 | 1064 | 1177 | 89.71332209 | 99.24114671 | 113 | 9.527824621 | 1061 | 116 | 3 | 6 | 8.454832456e-31 |

## timing

| backend | a_median_ms | b_median_ms | difference_ms | ratio | b_faster | b_faster_percent | wilcoxon_p | rank_biserial |
|---|---|---|---|---|---|---|---|---|
| cpu | 5.470723192 | 0.4780383333 | -4.832524189 | 0.078231628 | 1061 | 100 | 3.754886589e-175 | -1 |
| gpu | 2.973285079 | 2.831508333 | -0.09440464788 | 0.9823430671 | 604 | 56.92742696 | 4.486913348e-06 | -0.1625851318 |

## architecture

| flag | n | a_success | b_success | a_percent | b_percent | a_wilson_low_percent | a_wilson_high_percent | b_wilson_low_percent | b_wilson_high_percent | change_pp | recoveries | regressions |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| has_attention | 2 | 2 | 2 | 100 | 100 | 34.23802275 | 100 | 34.23802275 | 100 | 0 | 0 | 0 |
| is_transformer_like | 122 | 73 | 119 | 59.83606557 | 97.54098361 | 50.96537938 | 68.10623678 | 93.01924016 | 99.16023796 | 37.70491803 | 47 | 1 |
| has_residual_connections | 103 | 72 | 102 | 69.90291262 | 99.02912621 | 60.46054631 | 77.91407011 | 94.70418082 | 99.82841085 | 29.12621359 | 30 | 0 |
| is_resnet_like | 409 | 383 | 408 | 93.64303178 | 99.75550122 | 90.84863123 | 95.62524207 | 98.62823311 | 99.95682692 | 6.112469438 | 25 | 0 |
| is_vgg_like | 16 | 10 | 16 | 62.5 | 100 | 38.64104055 | 81.51876744 | 80.63923195 | 100 | 37.5 | 6 | 0 |
| is_mobilenet_like | 73 | 59 | 73 | 80.82191781 | 100 | 70.34449739 | 88.21763911 | 95.0007992 | 100 | 19.17808219 | 14 | 0 |

## reproducibility

| runtime | backend | n | median_percent | p95_percent |
|---|---|---|---|---|
| A | cpu | 1071 | 12.57832143 | 88.07889865 |
| A | gpu | 1071 | 9.793728668 | 77.50666948 |
| B | cpu | 1181 | 2.484854282 | 29.56023517 |
| B | gpu | 1181 | 4.404944378 | 54.1448249 |

## campaigns

| campaign | records | valid_completed_benchmarks | export_success | export_failure | validation_failure | failure_runtime_load_execution | failure_timeout | missing_results | unexpected_results | corrupt_or_incomplete_files | duplicate_results | cleanup_failure |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | 1762 | 1074 | 1195 | 567 | 4 | 106 | 11 | 0 | 0 | 0 | 0 | 0 |
| A2 | 1762 | 1071 | 1195 | 567 | 4 | 106 | 14 | 0 | 0 | 0 | 0 | 0 |
| A3 | 1762 | 1070 | 1195 | 567 | 4 | 106 | 15 | 0 | 0 | 0 | 0 | 0 |
| A4 | 1762 | 1068 | 1195 | 567 | 4 | 106 | 17 | 0 | 0 | 0 | 0 | 0 |
| A5 | 1762 | 1068 | 1195 | 567 | 4 | 105 | 18 | 0 | 0 | 0 | 0 | 0 |
| A6 | 1762 | 1067 | 1195 | 567 | 4 | 105 | 19 | 0 | 0 | 0 | 0 | 0 |
| B1 | 1762 | 1180 | 1190 | 572 | 4 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| B2 | 1762 | 1179 | 1190 | 572 | 4 | 7 | 0 | 0 | 0 | 0 | 0 | 0 |
| B3 | 1762 | 1181 | 1190 | 572 | 4 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| B4 | 1762 | 1180 | 1190 | 572 | 4 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| B5 | 1762 | 1181 | 1190 | 572 | 4 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| B6 | 1762 | 1181 | 1190 | 572 | 4 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |

## failures

| runtime | export | validation | timeout |
|---|---|---|---|
| 634 | 3402 | 24 | 94 |
| 34 | 3432 | 24 | 0 |

## complexity

| runtime | backend | feature | n | rho | p_value |
|---|---|---|---|---|---|
| A | cpu | flops | 1068 | 0.6233114717 | 5.437799705e-116 |
| A | cpu | total_params | 1068 | 0.6427019544 | 1.727953285e-125 |
| A | cpu | total_layers | 1068 | 0.6320770147 | 3.35571278e-120 |
| A | gpu | flops | 1068 | 0.6752968287 | 4.180356408e-143 |
| A | gpu | total_params | 1068 | 0.7854990094 | 2.149087075e-224 |
| A | gpu | total_layers | 1068 | 0.8123810177 | 6.046418416e-252 |
| B | cpu | flops | 1172 | 0.815387469 | 5.200581765e-280 |
| B | cpu | total_params | 1172 | 0.9061828859 | 0 |
| B | cpu | total_layers | 1172 | 0.8635808009 | 0 |
| B | gpu | flops | 1172 | 0.701187183 | 4.169293828e-174 |
| B | gpu | total_params | 1172 | 0.7873963287 | 4.461003444e-248 |
| B | gpu | total_layers | 1172 | 0.7497598723 | 4.71798126e-212 |

## pt_context

| backend | pt_median_ms | a_median_ms | a_ratio | a_rho | b_median_ms | b_ratio | b_rho | b_closer |
|---|---|---|---|---|---|---|---|---|
| cpu | 0.990304 | 5.470723192 | 6.242106406 | 0.7121326506 | 0.4827925 | 0.5915668787 | 0.9278397009 | 824 |
| gpu | 0.374899 | 2.9992764 | 7.451590694 | 0.8239383426 | 2.833964167 | 7.188193859 | 0.7886837647 |  |
