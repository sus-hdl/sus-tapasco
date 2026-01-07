SIM ?= icarus
TOPLEVEL_LANG ?= verilog
WAVES=1
VERILOG_SOURCES += $(PWD)/../../verilog/example.sv
TOPLEVEL = example
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
