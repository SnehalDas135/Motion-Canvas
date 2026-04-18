CXX      = g++
CXXFLAGS = -std=c++17 -O2 -Wall -fPIC
TARGET   = engine.so

SRCS = cpp/src/Detectors.cpp \
       cpp/src/FreeFaceEngine.cpp \
       cpp/engine_api.cpp

all: $(TARGET)
	@echo ""
	@echo "✓ Built $(TARGET) — ready for Python"
	@echo ""

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -shared -o $(TARGET) $(SRCS)

clean:
	rm -f $(TARGET)

.PHONY: all clean
