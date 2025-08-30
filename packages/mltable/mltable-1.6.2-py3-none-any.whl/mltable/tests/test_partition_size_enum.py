import pytest

from mltable.mltable import MLTablePartitionSize, UserErrorException


@pytest.mark.mltable_sdk_unit_test
class TestParitiontSizeEnum:

    def expected_unit(self, partition_size, partition_size_unit, expected_result):
        assert MLTablePartitionSize._parse(partition_size, partition_size_unit) == expected_result

    def expected_error(self, partition_size, partition_size_unit, msg):
        with pytest.raises(UserErrorException, match=msg):
            MLTablePartitionSize._parse(partition_size, partition_size_unit)

    def test_single_value(self):
        self.expected_unit(1000, MLTablePartitionSize.byte, 1000)

    def test_byte_enum(self):
        self.expected_unit(1, MLTablePartitionSize.byte, 1)

    def test_byte_string_abbv(self):
        self.expected_unit(10, 'b', 10)

    def test_byte_string_full(self):
        self.expected_unit(15, 'byte', 15)

    def test_kilobyte_enum(self):
        self.expected_unit(90, MLTablePartitionSize.kilobyte, 90 * 1024)

    def test_kilobyte_string_abbv(self):
        self.expected_unit(43, 'kb', 43 * 1024)

    def test_kilobyte_string_full(self):
        self.expected_unit(65, 'kilobyte', 65 * 1024)

    def test_megabyte_enum(self):
        self.expected_unit(87, MLTablePartitionSize.megabyte, 87 * 1024 * 1024)

    def test_megabyte_string_abbv(self):
        self.expected_unit(20, 'mb', 20 * 1024 * 1024)

    def test_megabyte_string_full(self):
        self.expected_unit(11, 'megabyte', 11 * 1024 * 1024)

    def test_gigabyte_enum(self):
        self.expected_unit(5, MLTablePartitionSize.gigabyte, 5 * 1024 * 1024 * 1024)

    def test_gigabyte_string_abbv(self):
        self.expected_unit(3, 'gb', 3 * 1024 * 1024 * 1024)

    def test_gigabyte_string_full(self):
        self.expected_unit(7, 'gigabyte', 7 * 1024 * 1024 * 1024)

    def test_invalid_unit(self):
        self.expected_error(8, 'terabyte',
                            'Expect `partition_size` unit to be a mltable.MLTablePartitionSizeUnit or.*')

    def test_non_int_value(self):
        self.expected_error('blah', 'mb', 'Expect `partition_size` to be a positive int.')

    def test_zero_value(self):
        self.expected_error(0, 'mb', 'Expect `partition_size` to be a positive int.')

    def test_negative_value(self):
        self.expected_error(-5, 'b', 'Expect `partition_size` to be a positive int.')
