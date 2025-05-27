MODULE_TOPDIR = ..

include $(MODULE_TOPDIR)/include/Make/Vars.make

DSTDIR = $(ARCH_DISTDIR)/jupyter

FILES = kernel.json startup.py grass_python.sh

default: install

$(DSTDIR):
	$(MKDIR) $@

install: $(DSTDIR)
	@for file in $(FILES); do \
		$(INSTALL_DATA) $$file $(DSTDIR)/$$file; \
	done
	@chmod +x $(DSTDIR)/grass_python.sh

	# Automatická registrace jupyter kernelu
	@echo "Registering GRASS Jupyter kernel..."
	@jupyter kernelspec install --user $(DSTDIR) --name grass --replace
