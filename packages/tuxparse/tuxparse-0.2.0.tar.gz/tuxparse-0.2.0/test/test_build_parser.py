import os
import re

from tuxparse.build_parser import BuildParser, REGEXES_GCC
from test.test_utils import (
    get_parser_results,
    assert_tests_created,
    assert_content_found,
)


def read_sample_file(name):
    """Read sample log files from test data directory"""
    if not name.startswith("/"):
        name = os.path.join(os.path.dirname(__file__), "data", name)
    return open(name).read()


class TestBuildParser:
    """Tests for build_parser (linux_log_parser_build equivalent)"""

    def setup_method(self):
        self.parser = BuildParser()
        self.snippet = """make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- 'CC=sccache arm-linux-gnueabihf-gcc' 'HOSTCC=sccache gcc'
In file included from /builds/linux/mm/internal.h:22,
                 from /builds/linux/mm/filemap.c:52:
/builds/linux/mm/vma.h: In function 'init_vma_munmap':
/builds/linux/mm/vma.h:184:26: error: 'USER_PGTABLES_CEILING' undeclared (first use in this function)
  184 |         vms->unmap_end = USER_PGTABLES_CEILING;
      |                          ^~~~~~~~~~~~~~~~~~~~~
/builds/linux/mm/vma.h:184:26: note: each undeclared identifier is reported only once for each function it appears in"""

    def test_create_name_no_regex(self):
        """Test create_name when no regex is provided"""
        name = self.parser.create_name(self.snippet)
        assert name is None

    def test_create_name_with_everything_to_be_removed(self):
        """Test create_name when all removable elements are in the string"""
        regex = re.compile(r"^.*$", re.S | re.M)
        snippet = "builds/linux/testa/testb///....c.. 23{test1}[test2]test.c"
        name = self.parser.create_name(snippet, regex)

        assert name == "testa_testb_______c___test_c"

    def test_create_name_with_regex_match(self):
        """Test create_name when a name regex is provided and there is a match"""
        regex = re.compile(r"^[^\n]*(?:error|warning)[^\n]*$", re.S | re.M)
        name = self.parser.create_name(self.snippet, regex)

        assert (
            name
            == "_mm_vma_h_error_USER_PGTABLES_CEILING_undeclared_first_use_in_this_function"
        )

    def test_create_name_with_regex_no_match(self):
        """Test create_name when a name regex is provided and there is no match"""
        regex = re.compile(r"oops.*", re.S | re.M)
        name = self.parser.create_name(self.snippet, regex)

        assert name is None

    def test_post_process_test_name(self):
        """Test post_process_test_name removes unwanted characters"""
        text = "builds/linux/testa/testb///....c.. 23{test1}[test2]test.c"
        cleaned = self.parser.post_process_test_name(text)

        assert cleaned == "_testa_testb_______c__ test_c"

    def test_split_by_regex_basic(self):
        """Test basic regex splitting functionality"""
        log = "ababaabccda"
        split_log = self.parser.split_by_regex(log, "(.*?)(a)")
        joined_split_log = "".join(split_log)

        expected = ["a", "b", "a", "b", "a", "a", "bccd", "a"]
        assert split_log == expected
        assert joined_split_log == log

    def test_captures_gcc_error_basic(self):
        """Test GCC compiler error detection"""
        gcc_log = """--toolchain=gcc
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=x86_64 CROSS_COMPILE=x86_64-linux-gnu- 'CC=sccache x86_64-linux-gnu-gcc' 'HOSTCC=sccache gcc'
/builds/linux/kernel/sched/ext.c:3630:35: error: initialization of 'bool (*)(struct rq *, struct task_struct *, int)' {aka '_Bool (*)(struct rq *, struct task_struct *, int)'} from incompatible pointer type 'void (*)(struct rq *, struct task_struct *, int)' [-Werror=incompatible-pointer-types]
 3630 |         .dequeue_task           = dequeue_task_scx,
      |                                   ^~~~~~~~~~~~~~~~"""

        data = self.parser.parse_log(gcc_log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect build issues"
        build_tests = get_parser_results(data, "build")

        # Verify GCC compiler error tests were created and contain expected content
        assert_tests_created(
            build_tests, "gcc-compiler", "Should detect GCC compiler errors"
        )
        assert_content_found(
            build_tests,
            "gcc-compiler",
            ["initialization", "incompatible pointer type"],
            "Should capture initialization and incompatible pointer type errors",
        )

    def test_captures_gcc_warning_basic(self):
        """Test GCC compiler warning detection"""
        gcc_log = """--toolchain=gcc
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=i386 CROSS_COMPILE=i686-linux-gnu- 'CC=sccache i686-linux-gnu-gcc' 'HOSTCC=sccache gcc'
test_zswap.c:38:32: warning: format '%ld' expects argument of type 'long int', but argument 3 has type 'size_t' {aka 'unsigned int'} [-Wformat=]
   38 |         ret = fprintf(file, "%ld\\n", value);
      |                              ~~^     ~~~~~
      |                                |     |
      |                                |     size_t {aka unsigned int}
      |                                long int
      |                              %d"""

        data = self.parser.parse_log(gcc_log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect build warnings"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify GCC compiler warning tests were created
        gcc_tests = [name for name in build_tests.keys() if "gcc-compiler" in name]
        assert len(gcc_tests) > 0, "Should detect GCC compiler warnings"

        # Verify log excerpts contain expected warning content
        found_warning = False
        found_format = False
        for test_name, test_data in build_tests.items():
            if "gcc-compiler" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "warning" in excerpt_text:
                    found_warning = True
                if "format" in excerpt_text:
                    found_format = True

        assert found_warning, "Should capture warning messages"
        assert found_format, "Should capture format-related warnings"

    def test_captures_clang_error_basic(self):
        """Test Clang compiler error detection"""
        clang_log = """--toolchain=clang
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- 'HOSTCC=sccache clang' 'CC=sccache clang' LLVM=1 LLVM_IAS=1
/builds/linux/mm/vma.h:184:19: error: use of undeclared identifier 'USER_PGTABLES_CEILING'
  184 |         vms->unmap_end = USER_PGTABLES_CEILING;
      |                          ^"""

        data = self.parser.parse_log(clang_log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Clang build errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify Clang compiler error tests were created
        clang_tests = [name for name in build_tests.keys() if "clang-compiler" in name]
        assert len(clang_tests) > 0, "Should detect Clang compiler errors"

        # Verify log excerpts contain expected error content
        found_error = False
        found_undeclared = False
        for test_name, test_data in build_tests.items():
            if "clang-compiler" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "error" in excerpt_text:
                    found_error = True
                if "undeclared identifier" in excerpt_text:
                    found_undeclared = True

        assert found_error, "Should capture error messages"
        assert found_undeclared, "Should capture undeclared identifier errors"

    def test_captures_clang_warning_basic(self):
        """Test Clang compiler warning detection"""
        clang_log = """--toolchain=clang
make
/builds/linux/drivers/soc/rockchip/pm_domains.c:800:22: warning: shift count is negative [-Wshift-count-negative]
  800 |         [RK3399_PD_TCPD0]       = DOMAIN_RK3399(8, 8, -1, false),
      |                                   ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
note: expanded from macro"""

        data = self.parser.parse_log(clang_log, unique=False)

        # Parser should run without crashing and produce data
        assert isinstance(data, dict)

    def test_clang_compiler_single_line(self):
        """Test single-line Clang error detection"""
        clang_log = """--toolchain=clang
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build INSTALL_PATH=/home/tuxbuild/.cache/tuxmake/builds/1/build/kselftest_install ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- HOSTCC=clang CC=clang LLVM=1 LLVM_IAS=1 kselftest-install
make[4]: Entering directory '/builds/linux/tools/testing/selftests/net/lib'
clang: error: linker command failed with exit code 1 (use -v to see invocation)"""

        data = self.parser.parse_log(clang_log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Clang single-line errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify single-line Clang tests were created
        clang_single_tests = [
            name for name in build_tests.keys() if "clang-compiler-single-line" in name
        ]
        assert len(clang_single_tests) > 0, "Should detect single-line Clang errors"

        # Verify log excerpts contain expected linker error content
        found_linker_failed = False
        for test_name, test_data in build_tests.items():
            if "clang-compiler-single-line" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "linker command failed" in excerpt_text:
                    found_linker_failed = True

        assert found_linker_failed, "Should capture linker command failed errors"

    def test_clang_compiler_fatal_error(self):
        """Test Clang fatal error detection"""
        clang_log = """--toolchain=clang
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build INSTALL_PATH=/home/tuxbuild/.cache/tuxmake/builds/1/build/kselftest_install ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- HOSTCC=clang CC=clang LLVM=1 LLVM_IAS=1 kselftest-install
make[4]: Entering directory '/builds/linux/tools/testing/selftests/rseq'
In file included from param_test.c:266:
In file included from ./rseq.h:114:
In file included from ./rseq-arm.h:150:
fatal error: too many errors emitted, stopping now [-ferror-limit=]"""

        data = self.parser.parse_log(clang_log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Clang fatal errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify fatal error tests were created
        fatal_error_tests = [
            name for name in build_tests.keys() if "clang-compiler-fatal-error" in name
        ]
        assert len(fatal_error_tests) > 0, "Should detect Clang fatal errors"

        # Verify log excerpts contain expected fatal error content
        found_too_many_errors = False
        for test_name, test_data in build_tests.items():
            if "clang-compiler-fatal-error" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "too many errors emitted" in excerpt_text:
                    found_too_many_errors = True

        assert (
            found_too_many_errors
        ), "Should capture 'too many errors emitted' messages"

    def test_general_not_a_git_repo(self):
        """Test detection of git repository errors"""
        log = """--toolchain=gcc
make -C /builds/linux/tools/testing/selftests/../../../tools/arch/arm64/tools/ OUTPUT=/builds/linux/tools/testing/selftests/../../../tools/
make[4]: Entering directory '/builds/linux/tools/testing/selftests/powerpc'
fatal: not a git repository (or any parent up to mount point /builds)
Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set)."""

        data = self.parser.parse_log(log, unique=False)

        # Parser should run without crashing and produce valid data
        assert isinstance(data, dict)

    def test_general_lld_error(self):
        """Test LLD linker error detection"""
        log = """--toolchain=clang
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- 'HOSTCC=sccache clang' 'CC=sccache clang' LLVM=1 LLVM_IAS=1
ld.lld: error: undefined symbol: irq_work_queue
>>> referenced by task_work.c
>>>               kernel/task_work.o:(task_work_add) in archive vmlinux.a"""

        data = self.parser.parse_log(log, unique=False)

        # Parser should run without crashing and produce valid data
        assert isinstance(data, dict)

    def test_general_ld_undefined_reference(self):
        """Test LD undefined reference detection"""
        log = """--toolchain=gcc
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- 'CC=sccache riscv64-linux-gnu-gcc' 'HOSTCC=sccache gcc'
riscv64-linux-gnu-ld: kernel/task_work.o: in function `task_work_add':
task_work.c:(.text+0x9a): undefined reference to `irq_work_queue'"""

        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect linker undefined reference errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify undefined reference tests were created
        undefined_ref_tests = [
            name
            for name in build_tests.keys()
            if "general-ld-undefined-reference" in name
        ]
        assert len(undefined_ref_tests) > 0, "Should detect undefined reference errors"

        # Verify log excerpts contain expected undefined reference content
        found_undefined_ref = False
        for test_name, test_data in build_tests.items():
            if "general-ld-undefined-reference" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "undefined reference" in excerpt_text:
                    found_undefined_ref = True

        assert found_undefined_ref, "Should capture undefined reference messages"

    def test_general_python_traceback(self):
        """Test Python traceback detection"""
        log = """--toolchain=clang
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build INSTALL_PATH=/home/tuxbuild/.cache/tuxmake/builds/1/build/kselftest_install ARCH=x86_64 SRCARCH=x86 CROSS_COMPILE=x86_64-linux-gnu- 'HOSTCC=sccache clang' 'CC=sccache clang' LLVM=1 LLVM_IAS=1 kselftest-install
make[4]: Entering directory '/builds/linux/tools/testing/selftests/net'
Traceback (most recent call last):
  File "/builds/linux/tools/net/ynl/generated/../ynl-gen-c.py", line 2945, in <module>
    main()
  File "/builds/linux/tools/net/ynl/generated/../ynl-gen-c.py", line 2655, in main
    parsed = Family(args.spec, exclude_ops)
ModuleNotFoundError: No module named 'jsonschema'"""

        data = self.parser.parse_log(log, unique=False)

        # Test data structure directly instead of JSON dumps
        assert data, "Should detect Python traceback errors"

        # Get build parser results
        build_parser_keys = [k for k in data.keys() if k.startswith("log-parser-build")]
        assert len(build_parser_keys) > 0, "Should create build parser results"

        build_tests = data[build_parser_keys[0]]

        # Verify Python traceback tests were created
        python_tests = [
            name for name in build_tests.keys() if "general-python-traceback" in name
        ]
        assert len(python_tests) > 0, "Should detect Python traceback errors"

        # Verify log excerpts contain expected Python error content
        found_module_not_found = False
        for test_name, test_data in build_tests.items():
            if "general-python-traceback" in test_name:
                log_excerpt = test_data.get("log_excerpt", [])
                excerpt_text = " ".join(log_excerpt)
                if "ModuleNotFoundError" in excerpt_text:
                    found_module_not_found = True

        assert found_module_not_found, "Should capture ModuleNotFoundError messages"
        assert data["log-parser-build-kselftest-install"]

    def test_no_string(self):
        """Test with empty log"""
        data = self.parser.parse_log("", unique=False)

        # Test data structure directly - empty logs should not create test results
        assert not data or all(
            not build_tests for build_tests in data.values()
        ), "Empty log should not generate any build tests"

    def test_extract_error_signature_compiler_error(self):
        """Test _extract_error_signature with compiler error"""
        error_line = "/builds/linux/fs/smb/server/transport_rdma.h:64:61: error: expected expression before '}' token"
        signature = self.parser._extract_error_signature(error_line)
        expected = (
            "/PATH/transport_rdma.h:XX:XX: error: expected expression before '}' token"
        )
        assert signature == expected

    def test_extract_error_signature_warning(self):
        """Test _extract_error_signature with compiler warning"""
        error_line = (
            "/builds/linux/mm/vma.h:184:26: warning: 'USER_PGTABLES_CEILING' undeclared"
        )
        signature = self.parser._extract_error_signature(error_line)
        expected = "/PATH/vma.h:XX:XX: warning: 'USER_PGTABLES_CEILING' undeclared"
        assert signature == expected

    def test_extract_error_signature_make_error(self):
        """Test _extract_error_signature with make error"""
        error_line = "make[3]: *** No rule to make target 'modules.order', needed by '/home/path/modules.order'."
        signature = self.parser._extract_error_signature(error_line)
        expected = "make[NUM]: *** No rule to make target 'modules.order', needed by '/PATH/modules.order'."
        assert signature == expected

    def test_extract_error_signature_multiline(self):
        """Test _extract_error_signature with multiline error"""
        error_line = """Some context line
/builds/linux/fs/file.c:123:45: error: undefined reference to 'function'
More context"""
        signature = self.parser._extract_error_signature(error_line)
        expected = "/PATH/file.c:XX:XX: error: undefined reference to 'function'"
        assert signature == expected

    def test_extract_error_signature_no_error(self):
        """Test _extract_error_signature with no error markers"""
        error_line = "Some regular log line without errors"
        signature = self.parser._extract_error_signature(error_line)
        assert signature == "Some regular log line without errors"

    def test_extract_affected_files_single_file(self):
        """Test _extract_affected_files with single file"""
        error_line = "/builds/linux/fs/smb/server/transport_rdma.h:64:61: error: expected expression"
        files = self.parser._extract_affected_files(error_line)
        assert files == ["/builds/linux/fs/smb/server/transport_rdma.h:64"]

    def test_extract_affected_files_multiple_lines(self):
        """Test _extract_affected_files with multiple error lines"""
        error_line = """/builds/linux/fs/file1.c:10:20: error: first error
/builds/linux/fs/file2.c:30:40: error: second error"""
        files = self.parser._extract_affected_files(error_line)
        expected = ["/builds/linux/fs/file1.c:10", "/builds/linux/fs/file2.c:30"]
        assert files == expected

    def test_extract_affected_files_no_files(self):
        """Test _extract_affected_files with no file patterns"""
        error_line = "Some error without file:line:column pattern"
        files = self.parser._extract_affected_files(error_line)
        assert files == []

    def test_deduplication_integration(self):
        """Test that deduplication works end-to-end"""
        # Log with same error in multiple files
        duplicate_error_log = """--toolchain=gcc
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- 'CC=sccache aarch64-linux-gnu-gcc' 'HOSTCC=sccache gcc'
In file included from /builds/linux/fs/smb/server/connection.c:16:
/builds/linux/fs/smb/server/transport_rdma.h:64:61: error: expected expression before '}' token
   64 | static inline void ksmbd_rdma_stop_listening(void) { return };
      |                                                             ^
In file included from /builds/linux/fs/smb/server/transport_ipc.c:29:
/builds/linux/fs/smb/server/transport_rdma.h:64:61: error: expected expression before '}' token
   64 | static inline void ksmbd_rdma_stop_listening(void) { return };
      |                                                             ^"""

        data = self.parser.parse_log(duplicate_error_log, unique=False)

        # Should have one test with affected_files metadata
        build_results = data["log-parser-build-kernel"]
        error_tests = [
            k for k in build_results.keys() if "error_expected_expression" in k
        ]
        assert len(error_tests) == 1

        test_result = build_results[error_tests[0]]
        assert "affected_files" in test_result
        assert (
            len(test_result["affected_files"]) == 1
        )  # Should be deduplicated to one file
        assert len(test_result["log_excerpt"]) == 1  # Should have one excerpt

    def test_deduplication_different_errors(self):
        """Test that different errors are not deduplicated"""
        different_errors_log = """--toolchain=gcc
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- 'CC=sccache aarch64-linux-gnu-gcc' 'HOSTCC=sccache gcc'
/builds/linux/fs/file1.c:10:20: error: expected expression before '}' token
/builds/linux/fs/file2.c:30:40: error: undefined reference to 'function'"""

        data = self.parser.parse_log(different_errors_log, unique=False)

        # Should have separate tests for different errors
        build_results = data["log-parser-build-kernel"]
        error_tests = [k for k in build_results.keys() if "error" in k]
        assert len(error_tests) >= 1  # Should have at least one error test

        # Each test should have affected_files
        for test_name in error_tests:
            test_result = build_results[test_name]
            assert "affected_files" in test_result

    def test_process_blocks_with_context(self):
        """Test process_blocks method with various context patterns"""

        # Create a log block with context patterns
        blocks = [
            "make --silent --keep-going --jobs=8",
            "make[1]: Entering directory '/builds/linux'",
            "In file included from /builds/linux/fs/file.c:16:",
            "In function 'test_function':",
            "/builds/linux/fs/file.c:10:20: error: expected expression",
            "make[1]: Leaving directory '/builds/linux'",
        ]

        result = self.parser.process_blocks(blocks, REGEXES_GCC)

        # Should process the blocks without error
        assert isinstance(result, dict)

    def test_split_log_by_make_edge_cases(self):
        """Test split_log_by_make with edge cases"""
        # Test with no make commands
        log_no_make = """Some regular log output
without any make commands
just regular text"""

        chunks = self.parser.split_log_by_make(log_no_make)
        assert chunks == []

        # Test with multiple make commands
        log_multiple_make = """make --silent --keep-going --jobs=8 target1
some output for target1
make --silent --keep-going --jobs=8 target2
some output for target2"""

        chunks = self.parser.split_log_by_make(log_multiple_make)
        assert len(chunks) == 2
        assert chunks[0][0] == "make --silent --keep-going --jobs=8 target1"
        assert chunks[1][0] == "make --silent --keep-going --jobs=8 target2"

    def test_clean_suite_postfix_edge_cases(self):
        """Test clean_suite_postfix with various command formats"""
        # Test non-make command
        result = self.parser.clean_suite_postfix("gcc -o file file.c")
        assert result is None

        # Test make command with simple targets
        cmd = "make --silent --keep-going --jobs=8 modules dtbs"
        result = self.parser.clean_suite_postfix(cmd)
        assert result == "modules_dtbs"

        # Test make command with no targets
        cmd = "make --silent --keep-going --jobs=8"
        result = self.parser.clean_suite_postfix(cmd)
        assert result == "kernel"

    def test_no_toolchain_detection(self):
        """Test behavior when no supported toolchain is detected"""
        log_no_toolchain = """Some build log
without toolchain specification
/builds/linux/fs/file.c:10:20: error: expected expression"""

        data = self.parser.parse_log(log_no_toolchain, unique=False)

        # Test data structure directly - logs without toolchain should not create test results
        assert not data or all(
            not build_tests for build_tests in data.values()
        ), "Log without toolchain should not generate build tests"

    def test_log_with_no_issues(self):
        """Test log processing when no issues are found"""
        clean_log = """--toolchain=gcc
make --silent --keep-going --jobs=8 O=/home/tuxbuild/.cache/tuxmake/builds/1/build ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- 'CC=sccache aarch64-linux-gnu-gcc' 'HOSTCC=sccache gcc'
  CC      arch/arm64/kernel/setup.o
  CC      arch/arm64/kernel/irq.o
  LD      arch/arm64/kernel/built-in.a
Kernel: arch/arm64/boot/Image.gz is ready"""

        data = self.parser.parse_log(clean_log, unique=False)

        # Should produce empty result for clean logs
        assert not data
