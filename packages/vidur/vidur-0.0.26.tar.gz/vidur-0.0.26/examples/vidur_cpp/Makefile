# Build using CMake
BUILD_DIR = build

.PHONY: all clean

all: $(BUILD_DIR)
	cd $(BUILD_DIR) && cmake .. && make

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
