from datetime import timedelta, datetime, time, tzinfo
from enum import IntEnum, unique
from typing import List, Any, Dict, Tuple, Optional

from data_aggregator_sdk.integration_message import IntegrationV0MessageData, IntegrationV0MessageProfile, ProfileGranulation, GRANULATION_TO_END_OF_DATETIME_MAP, ProfileKind
from data_aggregator_sdk.utils.round_dt import round_dt

from data_gateway_sdk.utils.buf_ref import BufRef
from data_gateway_sdk.utils.days_ago_calculation import days_ago_calculation
from data_gateway_sdk.utils.packet import Packet
from data_gateway_sdk.utils.true_round import true_round


# PACKET (128 bits)   smpm_ul_device_energy_16b_profile_8h_pqs
#
# RESULT int:        16227037341613019245223190382775473
# RESULT bin:  MSB   00000000 00000011 00100000 00001110 00000001 10000000 00101000 00000100 00000000 01100000 00001000 00000000 10000000 00000000 00001100 10110001   LSB
# RESULT hex:  LE    b1 0c 00 80 00 08 60 00 04 28 80 01 0e 20 03 00
#
# name                  type       size  value(int)                                                                                                                        data(bits)   # noqa: E501
# --------------------  ---------  ----  ----------  --------------------------------------------------------------------------------------------------------------------------------   # noqa: E501
# packet_type_id.0.VAL  u7            7          49                                                                                                                           0110001   # noqa: E501
# packet_type_id.0.DFF  bool          1           1                                                                                                                          1
# packet_type_id.1.VAL  u2            2           0                                                                                                                        00
# packet_type_id.1.DFF  bool          1           1                                                                                                                       1
# packet_type_id.2.VAL  u2            2           1                                                                                                                     01
# packet_type_id.2.DFF  bool          1           0                                                                                                                    0
# days_ago              timedelta     6           0                                                                                                              000000
# profile.0.point       u11          11           0                                                                                                   00000000000
# profile.1.point       u11          11           1                                                                                        00000000001
# profile.2.point       u11          11           2                                                                             00000000010
# profile.3.point       u11          11           3                                                                  00000000011
# profile.4.point       u11          11           4                                                       00000000100
# profile.5.point       u11          11           5                                            00000000101
# profile.6.point       u11          11           6                                 00000000110
# profile.7.point       u11          11           7                      00000000111
# point_factor          uf12p1       12          50          000000110010
# RESERVED              u8            8           0  00000000

@unique
class SmpmUlDeviceEnergy16bProfile8hPQSIds(IntEnum):
    UL_DATA_16B__PROFILE_H8_1_S__AVG = 561
    UL_DATA_16B__PROFILE_H8_1_S__AVG__PHASE_A = 562
    UL_DATA_16B__PROFILE_H8_1_S__AVG__PHASE_B = 563
    UL_DATA_16B__PROFILE_H8_1_S__AVG__PHASE_C = 564
    UL_DATA_16B__PROFILE_H8_1_S__MIN = 565
    UL_DATA_16B__PROFILE_H8_1_S__MIN__PHASE_A = 566
    UL_DATA_16B__PROFILE_H8_1_S__MIN__PHASE_B = 567
    UL_DATA_16B__PROFILE_H8_1_S__MIN__PHASE_C = 568
    UL_DATA_16B__PROFILE_H8_1_S__MAX = 569
    UL_DATA_16B__PROFILE_H8_1_S__MAX__PHASE_A = 570
    UL_DATA_16B__PROFILE_H8_1_S__MAX__PHASE_B = 571
    UL_DATA_16B__PROFILE_H8_1_S__MAX__PHASE_C = 572
    UL_DATA_16B__PROFILE_H8_1_P__AVG = 573
    UL_DATA_16B__PROFILE_H8_1_P__AVG__PHASE_A = 574
    UL_DATA_16B__PROFILE_H8_1_P__AVG__PHASE_B = 575
    UL_DATA_16B__PROFILE_H8_1_P__AVG__PHASE_C = 576
    UL_DATA_16B__PROFILE_H8_1_P__MIN = 577
    UL_DATA_16B__PROFILE_H8_1_P__MIN__PHASE_A = 578
    UL_DATA_16B__PROFILE_H8_1_P__MIN__PHASE_B = 579
    UL_DATA_16B__PROFILE_H8_1_P__MIN__PHASE_C = 580
    UL_DATA_16B__PROFILE_H8_1_P__MAX = 581
    UL_DATA_16B__PROFILE_H8_1_P__MAX__PHASE_A = 582
    UL_DATA_16B__PROFILE_H8_1_P__MAX__PHASE_B = 583
    UL_DATA_16B__PROFILE_H8_1_P__MAX__PHASE_C = 584
    UL_DATA_16B__PROFILE_H8_1_Q__AVG = 585
    UL_DATA_16B__PROFILE_H8_1_Q__AVG__PHASE_A = 586
    UL_DATA_16B__PROFILE_H8_1_Q__AVG__PHASE_B = 587
    UL_DATA_16B__PROFILE_H8_1_Q__AVG__PHASE_C = 588
    UL_DATA_16B__PROFILE_H8_1_Q__MIN = 589
    UL_DATA_16B__PROFILE_H8_1_Q__MIN__PHASE_A = 590
    UL_DATA_16B__PROFILE_H8_1_Q__MIN__PHASE_B = 591
    UL_DATA_16B__PROFILE_H8_1_Q__MIN__PHASE_C = 592
    UL_DATA_16B__PROFILE_H8_1_Q__MAX = 593
    UL_DATA_16B__PROFILE_H8_1_Q__MAX__PHASE_A = 594
    UL_DATA_16B__PROFILE_H8_1_Q__MAX__PHASE_B = 595
    UL_DATA_16B__PROFILE_H8_1_Q__MAX__PHASE_C = 596
    UL_DATA_16B__PROFILE_H8_2_S__AVG = 597
    UL_DATA_16B__PROFILE_H8_2_S__AVG__PHASE_A = 598
    UL_DATA_16B__PROFILE_H8_2_S__AVG__PHASE_B = 599
    UL_DATA_16B__PROFILE_H8_2_S__AVG__PHASE_C = 600
    UL_DATA_16B__PROFILE_H8_2_S__MIN = 601
    UL_DATA_16B__PROFILE_H8_2_S__MIN__PHASE_A = 602
    UL_DATA_16B__PROFILE_H8_2_S__MIN__PHASE_B = 603
    UL_DATA_16B__PROFILE_H8_2_S__MIN__PHASE_C = 604
    UL_DATA_16B__PROFILE_H8_2_S__MAX = 605
    UL_DATA_16B__PROFILE_H8_2_S__MAX__PHASE_A = 606
    UL_DATA_16B__PROFILE_H8_2_S__MAX__PHASE_B = 607
    UL_DATA_16B__PROFILE_H8_2_S__MAX__PHASE_C = 608
    UL_DATA_16B__PROFILE_H8_2_P__AVG = 609
    UL_DATA_16B__PROFILE_H8_2_P__AVG__PHASE_A = 610
    UL_DATA_16B__PROFILE_H8_2_P__AVG__PHASE_B = 611
    UL_DATA_16B__PROFILE_H8_2_P__AVG__PHASE_C = 612
    UL_DATA_16B__PROFILE_H8_2_P__MIN = 613
    UL_DATA_16B__PROFILE_H8_2_P__MIN__PHASE_A = 614
    UL_DATA_16B__PROFILE_H8_2_P__MIN__PHASE_B = 615
    UL_DATA_16B__PROFILE_H8_2_P__MIN__PHASE_C = 616
    UL_DATA_16B__PROFILE_H8_2_P__MAX = 617
    UL_DATA_16B__PROFILE_H8_2_P__MAX__PHASE_A = 618
    UL_DATA_16B__PROFILE_H8_2_P__MAX__PHASE_B = 619
    UL_DATA_16B__PROFILE_H8_2_P__MAX__PHASE_C = 620
    UL_DATA_16B__PROFILE_H8_2_Q__AVG = 621
    UL_DATA_16B__PROFILE_H8_2_Q__AVG__PHASE_A = 622
    UL_DATA_16B__PROFILE_H8_2_Q__AVG__PHASE_B = 623
    UL_DATA_16B__PROFILE_H8_2_Q__AVG__PHASE_C = 624
    UL_DATA_16B__PROFILE_H8_2_Q__MIN = 625
    UL_DATA_16B__PROFILE_H8_2_Q__MIN__PHASE_A = 626
    UL_DATA_16B__PROFILE_H8_2_Q__MIN__PHASE_B = 627
    UL_DATA_16B__PROFILE_H8_2_Q__MIN__PHASE_C = 628
    UL_DATA_16B__PROFILE_H8_2_Q__MAX = 629
    UL_DATA_16B__PROFILE_H8_2_Q__MAX__PHASE_A = 630
    UL_DATA_16B__PROFILE_H8_2_Q__MAX__PHASE_B = 631
    UL_DATA_16B__PROFILE_H8_2_Q__MAX__PHASE_C = 632
    UL_DATA_16B__PROFILE_H8_3_S__AVG = 633
    UL_DATA_16B__PROFILE_H8_3_S__AVG__PHASE_A = 634
    UL_DATA_16B__PROFILE_H8_3_S__AVG__PHASE_B = 635
    UL_DATA_16B__PROFILE_H8_3_S__AVG__PHASE_C = 636
    UL_DATA_16B__PROFILE_H8_3_S__MIN = 637
    UL_DATA_16B__PROFILE_H8_3_S__MIN__PHASE_A = 638
    UL_DATA_16B__PROFILE_H8_3_S__MIN__PHASE_B = 639
    UL_DATA_16B__PROFILE_H8_3_S__MIN__PHASE_C = 640
    UL_DATA_16B__PROFILE_H8_3_S__MAX = 641
    UL_DATA_16B__PROFILE_H8_3_S__MAX__PHASE_A = 642
    UL_DATA_16B__PROFILE_H8_3_S__MAX__PHASE_B = 643
    UL_DATA_16B__PROFILE_H8_3_S__MAX__PHASE_C = 644
    UL_DATA_16B__PROFILE_H8_3_P__AVG = 645
    UL_DATA_16B__PROFILE_H8_3_P__AVG__PHASE_A = 646
    UL_DATA_16B__PROFILE_H8_3_P__AVG__PHASE_B = 647
    UL_DATA_16B__PROFILE_H8_3_P__AVG__PHASE_C = 648
    UL_DATA_16B__PROFILE_H8_3_P__MIN = 649
    UL_DATA_16B__PROFILE_H8_3_P__MIN__PHASE_A = 650
    UL_DATA_16B__PROFILE_H8_3_P__MIN__PHASE_B = 651
    UL_DATA_16B__PROFILE_H8_3_P__MIN__PHASE_C = 652
    UL_DATA_16B__PROFILE_H8_3_P__MAX = 653
    UL_DATA_16B__PROFILE_H8_3_P__MAX__PHASE_A = 654
    UL_DATA_16B__PROFILE_H8_3_P__MAX__PHASE_B = 655
    UL_DATA_16B__PROFILE_H8_3_P__MAX__PHASE_C = 656
    UL_DATA_16B__PROFILE_H8_3_Q__AVG = 657
    UL_DATA_16B__PROFILE_H8_3_Q__AVG__PHASE_A = 658
    UL_DATA_16B__PROFILE_H8_3_Q__AVG__PHASE_B = 659
    UL_DATA_16B__PROFILE_H8_3_Q__AVG__PHASE_C = 660
    UL_DATA_16B__PROFILE_H8_3_Q__MIN = 661
    UL_DATA_16B__PROFILE_H8_3_Q__MIN__PHASE_A = 662
    UL_DATA_16B__PROFILE_H8_3_Q__MIN__PHASE_B = 663
    UL_DATA_16B__PROFILE_H8_3_Q__MIN__PHASE_C = 664
    UL_DATA_16B__PROFILE_H8_3_Q__MAX = 665
    UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_A = 666
    UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_B = 667
    UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C = 668


PROFILE_H8_PQS_TYPE_MAP = {
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG: ProfileKind.FULL_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG__PHASE_A: ProfileKind.FULL_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG__PHASE_B: ProfileKind.FULL_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__AVG__PHASE_C: ProfileKind.FULL_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MIN: ProfileKind.FULL_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MIN__PHASE_A: ProfileKind.FULL_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MIN__PHASE_B: ProfileKind.FULL_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MIN__PHASE_C: ProfileKind.FULL_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MAX: ProfileKind.FULL_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MAX__PHASE_A: ProfileKind.FULL_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MAX__PHASE_B: ProfileKind.FULL_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_S__MAX__PHASE_C: ProfileKind.FULL_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__AVG: ProfileKind.ACTIVE_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__AVG__PHASE_A: ProfileKind.ACTIVE_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__AVG__PHASE_B: ProfileKind.ACTIVE_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__AVG__PHASE_C: ProfileKind.ACTIVE_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MIN: ProfileKind.ACTIVE_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MIN__PHASE_A: ProfileKind.ACTIVE_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MIN__PHASE_B: ProfileKind.ACTIVE_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MIN__PHASE_C: ProfileKind.ACTIVE_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MAX: ProfileKind.ACTIVE_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MAX__PHASE_A: ProfileKind.ACTIVE_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MAX__PHASE_B: ProfileKind.ACTIVE_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_P__MAX__PHASE_C: ProfileKind.ACTIVE_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__AVG: ProfileKind.REACTIVE_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__AVG__PHASE_A: ProfileKind.REACTIVE_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__AVG__PHASE_B: ProfileKind.REACTIVE_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__AVG__PHASE_C: ProfileKind.REACTIVE_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MIN: ProfileKind.REACTIVE_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MIN__PHASE_A: ProfileKind.REACTIVE_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MIN__PHASE_B: ProfileKind.REACTIVE_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MIN__PHASE_C: ProfileKind.REACTIVE_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MAX: ProfileKind.REACTIVE_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MAX__PHASE_A: ProfileKind.REACTIVE_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MAX__PHASE_B: ProfileKind.REACTIVE_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_1_Q__MAX__PHASE_C: ProfileKind.REACTIVE_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__AVG: ProfileKind.FULL_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__AVG__PHASE_A: ProfileKind.FULL_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__AVG__PHASE_B: ProfileKind.FULL_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__AVG__PHASE_C: ProfileKind.FULL_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MIN: ProfileKind.FULL_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MIN__PHASE_A: ProfileKind.FULL_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MIN__PHASE_B: ProfileKind.FULL_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MIN__PHASE_C: ProfileKind.FULL_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MAX: ProfileKind.FULL_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MAX__PHASE_A: ProfileKind.FULL_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MAX__PHASE_B: ProfileKind.FULL_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_S__MAX__PHASE_C: ProfileKind.FULL_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__AVG: ProfileKind.ACTIVE_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__AVG__PHASE_A: ProfileKind.ACTIVE_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__AVG__PHASE_B: ProfileKind.ACTIVE_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__AVG__PHASE_C: ProfileKind.ACTIVE_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MIN: ProfileKind.ACTIVE_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MIN__PHASE_A: ProfileKind.ACTIVE_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MIN__PHASE_B: ProfileKind.ACTIVE_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MIN__PHASE_C: ProfileKind.ACTIVE_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MAX: ProfileKind.ACTIVE_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MAX__PHASE_A: ProfileKind.ACTIVE_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MAX__PHASE_B: ProfileKind.ACTIVE_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_P__MAX__PHASE_C: ProfileKind.ACTIVE_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__AVG: ProfileKind.REACTIVE_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__AVG__PHASE_A: ProfileKind.REACTIVE_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__AVG__PHASE_B: ProfileKind.REACTIVE_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__AVG__PHASE_C: ProfileKind.REACTIVE_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MIN: ProfileKind.REACTIVE_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MIN__PHASE_A: ProfileKind.REACTIVE_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MIN__PHASE_B: ProfileKind.REACTIVE_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MIN__PHASE_C: ProfileKind.REACTIVE_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MAX: ProfileKind.REACTIVE_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MAX__PHASE_A: ProfileKind.REACTIVE_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MAX__PHASE_B: ProfileKind.REACTIVE_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_2_Q__MAX__PHASE_C: ProfileKind.REACTIVE_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__AVG: ProfileKind.FULL_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__AVG__PHASE_A: ProfileKind.FULL_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__AVG__PHASE_B: ProfileKind.FULL_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__AVG__PHASE_C: ProfileKind.FULL_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MIN: ProfileKind.FULL_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MIN__PHASE_A: ProfileKind.FULL_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MIN__PHASE_B: ProfileKind.FULL_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MIN__PHASE_C: ProfileKind.FULL_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MAX: ProfileKind.FULL_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MAX__PHASE_A: ProfileKind.FULL_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MAX__PHASE_B: ProfileKind.FULL_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_S__MAX__PHASE_C: ProfileKind.FULL_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__AVG: ProfileKind.ACTIVE_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__AVG__PHASE_A: ProfileKind.ACTIVE_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__AVG__PHASE_B: ProfileKind.ACTIVE_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__AVG__PHASE_C: ProfileKind.ACTIVE_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MIN: ProfileKind.ACTIVE_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MIN__PHASE_A: ProfileKind.ACTIVE_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MIN__PHASE_B: ProfileKind.ACTIVE_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MIN__PHASE_C: ProfileKind.ACTIVE_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MAX: ProfileKind.ACTIVE_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MAX__PHASE_A: ProfileKind.ACTIVE_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MAX__PHASE_B: ProfileKind.ACTIVE_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_P__MAX__PHASE_C: ProfileKind.ACTIVE_POWER_MAX_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__AVG: ProfileKind.REACTIVE_POWER_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__AVG__PHASE_A: ProfileKind.REACTIVE_POWER_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__AVG__PHASE_B: ProfileKind.REACTIVE_POWER_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__AVG__PHASE_C: ProfileKind.REACTIVE_POWER_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MIN: ProfileKind.REACTIVE_POWER_MIN_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MIN__PHASE_A: ProfileKind.REACTIVE_POWER_MIN_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MIN__PHASE_B: ProfileKind.REACTIVE_POWER_MIN_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MIN__PHASE_C: ProfileKind.REACTIVE_POWER_MIN_C,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX: ProfileKind.REACTIVE_POWER_MAX_ABC,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_A: ProfileKind.REACTIVE_POWER_MAX_A,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_B: ProfileKind.REACTIVE_POWER_MAX_B,
    SmpmUlDeviceEnergy16bProfile8hPQSIds.UL_DATA_16B__PROFILE_H8_3_Q__MAX__PHASE_C: ProfileKind.REACTIVE_POWER_MAX_C,
}


class SmpmUlDeviceEnergy16BProfile8HPqsData(Packet):
    packet_type_id: SmpmUlDeviceEnergy16bProfile8hPQSIds
    days_ago: timedelta
    profile: Tuple[int, int, int, int, int, int, int, int]
    point_factor: float

    def serialize(self) -> bytes:
        data = self
        result = 0
        size = 0
        packet_type_id__value_int_tmp1 = 0
        packet_type_id__value_size_tmp2 = 0
        assert isinstance(data.packet_type_id, SmpmUlDeviceEnergy16bProfile8hPQSIds)
        packet_type_id__value_int_tmp1 |= ((data.packet_type_id.value) & (2 ** (10) - 1)) << packet_type_id__value_size_tmp2
        packet_type_id__value_size_tmp2 += 10
        packet_type_id__max_size_tmp3 = 0
        packet_type_id__steps_tmp4 = [8, 3, 3, 3]
        for packet_type_id__j_tmp5 in range(32):
            packet_type_id__step_tmp6 = packet_type_id__steps_tmp4[packet_type_id__j_tmp5] if packet_type_id__j_tmp5 < len(packet_type_id__steps_tmp4) else packet_type_id__steps_tmp4[-1]  # noqa: E501
            packet_type_id__max_size_tmp3 += packet_type_id__step_tmp6
            packet_type_id__current_part_value_tmp7 = packet_type_id__value_int_tmp1 & (2 ** packet_type_id__step_tmp6 - 1)
            packet_type_id__value_int_tmp1 = packet_type_id__value_int_tmp1 >> (packet_type_id__step_tmp6 - 1)
            result |= ((packet_type_id__current_part_value_tmp7) & (2 ** ((packet_type_id__step_tmp6 - 1)) - 1)) << size
            size += (packet_type_id__step_tmp6 - 1)
            assert isinstance((packet_type_id__value_int_tmp1 != 0), bool)
            result |= ((int((packet_type_id__value_int_tmp1 != 0))) & (2 ** (1) - 1)) << size
            size += 1
            if packet_type_id__value_int_tmp1 == 0:
                break
        isinstance(data.days_ago, (int, timedelta))
        days_ago_tmp8 = int(data.days_ago.total_seconds() // 86400 if isinstance(data.days_ago, timedelta) else data.days_ago // 86400)
        assert 0 <= days_ago_tmp8 <= 63
        result |= ((days_ago_tmp8) & (2 ** (6) - 1)) << size
        size += 6
        assert isinstance(data.profile, tuple) and len(data.profile) == 8
        assert isinstance(data.profile[0], int)
        assert 0 <= data.profile[0] <= 4095
        result |= ((data.profile[0]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[1], int)
        assert 0 <= data.profile[1] <= 4095
        result |= ((data.profile[1]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[2], int)
        assert 0 <= data.profile[2] <= 4095
        result |= ((data.profile[2]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[3], int)
        assert 0 <= data.profile[3] <= 4095
        result |= ((data.profile[3]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[4], int)
        assert 0 <= data.profile[4] <= 4095
        result |= ((data.profile[4]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[5], int)
        assert 0 <= data.profile[5] <= 4095
        result |= ((data.profile[5]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[6], int)
        assert 0 <= data.profile[6] <= 4095
        result |= ((data.profile[6]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.profile[7], int)
        assert 0 <= data.profile[7] <= 4095
        result |= ((data.profile[7]) & (2 ** (12) - 1)) << size
        size += 12
        assert isinstance(data.point_factor, (int, float))
        assert 0.0 <= data.point_factor <= 40.95
        result |= ((int(round(float(data.point_factor) * 100.0, 0))) & (2 ** (12) - 1)) << size
        size += 12
        return result.to_bytes(16, "little")

    @classmethod
    def parse(cls, buf: BufRef) -> 'SmpmUlDeviceEnergy16BProfile8HPqsData':
        result__el_tmp9: Dict[str, Any] = dict()
        packet_type_id__res_tmp10 = 0
        packet_type_id__steps_tmp11 = (8, 3, 3, 3)
        packet_type_id__res_size_tmp12 = 0
        packet_type_id__step_tmp13 = 0
        for packet_type_id__i_tmp15 in range(32):
            packet_type_id__step_tmp13 = (packet_type_id__steps_tmp11[packet_type_id__i_tmp15] if packet_type_id__i_tmp15 < len(packet_type_id__steps_tmp11) else packet_type_id__steps_tmp11[-1]) - 1  # noqa: E501
            packet_type_id__res_tmp10 |= buf.shift(packet_type_id__step_tmp13) << packet_type_id__res_size_tmp12
            packet_type_id__res_size_tmp12 += packet_type_id__step_tmp13
            packet_type_id__dff_tmp14 = bool(buf.shift(1))
            if not packet_type_id__dff_tmp14:
                break
        packet_type_id__buf_tmp16 = buf
        buf = BufRef(packet_type_id__res_tmp10, stop_on_buffer_end=True)
        result__el_tmp9["packet_type_id"] = SmpmUlDeviceEnergy16bProfile8hPQSIds(buf.shift(10))
        buf = packet_type_id__buf_tmp16
        result__el_tmp9["days_ago"] = timedelta(seconds=buf.shift(6) * 86400)
        profile_tmp17: List[int] = []
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        profile__item_tmp18 = buf.shift(12) + 0
        profile_tmp17.append(profile__item_tmp18)
        result__el_tmp9["profile"] = tuple(profile_tmp17)
        result__el_tmp9["point_factor"] = round(buf.shift(12) / 100.0, 2)
        result = SmpmUlDeviceEnergy16BProfile8HPqsData(**result__el_tmp9)
        return result

    def to_integration_data(self, received_at: datetime, device_tz: tzinfo, **kwargs: Any) -> List[IntegrationV0MessageData]:
        values: Tuple[Optional[float], ...]
        profiles = (
            true_round(self.profile[0] * self.point_factor) / 1000,
            true_round(self.profile[1] * self.point_factor) / 1000,
            true_round(self.profile[2] * self.point_factor) / 1000,
            true_round(self.profile[3] * self.point_factor) / 1000,
            true_round(self.profile[4] * self.point_factor) / 1000,
            true_round(self.profile[5] * self.point_factor) / 1000,
            true_round(self.profile[6] * self.point_factor) / 1000,
            true_round(self.profile[7] * self.point_factor) / 1000,
        )
        if self.packet_type_id in {561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579,
                                   580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596}:
            values = (
                *profiles,
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
            )
        elif self.packet_type_id in {597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615,
                                     616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632}:
            values = (
                None, None, None, None, None, None, None, None,
                *profiles,
                None, None, None, None, None, None, None, None,
            )
        else:
            values = (
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
                *profiles,
            )
        return [
            IntegrationV0MessageData(
                dt=round_dt(
                    days_ago_calculation(
                        received_at,
                        device_tz,
                        time(0),
                        self.days_ago,
                    ),
                    GRANULATION_TO_END_OF_DATETIME_MAP[ProfileGranulation.MINUTE_60],
                ),
                profiles=[
                    IntegrationV0MessageProfile(
                        type=PROFILE_H8_PQS_TYPE_MAP[self.packet_type_id],
                        granulation=ProfileGranulation.MINUTE_60,
                        values=values,
                    ),
                ],
            ),
        ]
