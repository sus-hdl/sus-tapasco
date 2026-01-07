BASE ?=example

all: verilog

verilog:
	rm -rf verilog
	mkdir verilog
	sus_compiler --top $(BASE) -o verilog/$(BASE).sv sus/*

verilog_cocotb: verilog
	sed -i "s/always_comb/always @(*)/" verilog/$(BASE).sv

ipxact/array_init_update_sum.zip:
	sed -i "s/ 4294967296/ 33'd4294967296/" verilog/array_init_update_sum.sv
	python3 ipxact.py -n array_init_update_sum -t array_init_update_sum -f verilog/array_init_update_sum.sv -d verilog

ipxact/ethernet_example.zip:
	sed -i "s/ 4294967296/ 33'd4294967296/" verilog/ethernet_example.sv
	python3 ipxact.py -n ethernet_example -t ethernet_example -f verilog/ethernet_example.sv -d verilog

tapasco_ddr: ipxact/array_init_update_sum.zip
	tapasco import ipxact/array_init_update_sum.zip as 100 -p AU280
	tapasco --jobsFile ddr.json

tapasco_eth: ipxact/ethernet_example.zip
	tapasco import ipxact/ethernet_example.zip as 100 -p AU280
	tapasco --jobsFile eth.json

tapasco_hbm: ipxact/array_init_update_sum.zip
	tapasco import ipxact/array_init_update_sum.zip as 100 -p AU280
	tapasco --jobsFile hbm.json

clean:
	rm -rf verilog/ ipxact/

.PHONY: all verilog verilog_cocotb ipxact tapasco_ddr tapasco_eth tapasco_hbm clean
