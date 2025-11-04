all: verilog

verilog:
	mkdir -p verilog
	sus_compiler -o verilog/example.sv

verilog_cocotb: verilog
	sed -i "s/always_comb/always @(*)/" verilog/example.sv

ipxact: verilog
	python3 ipxact.py -n example -t example -f verilog/example.sv -d verilog

tapasco: ipxact
	tapasco import ipxact/example.zip as 100 -p AU280
	tapasco compose [example x1]@100MHz -p AU280 --deleteProjects false

.PHONY: all verilog verilog_cocotb ipxact tapasco
