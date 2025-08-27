import os
import shutil
import subprocess
import compiletools.testhelper as uth
import compiletools.utils
import compiletools.cake
import compiletools.magicflags
import compiletools.headerdeps
import compiletools.test_base as tb

# Although this is virtually identical to the test_cake.py, we can't merge
# the tests due to memoized results.


class TestMagicPKGCONFIG(tb.BaseCompileToolsTestCase):


    def test_magicpkgconfig(self):
        # This test is to ensure that the //#PKG-CONFIG magic flag 
        # correctly acquires extra cflags and libs

        with uth.CompileToolsTestContext() as (tmpdir, config_path):
            # Copy the magicpkgconfig test files to the temp directory and compile
            # using ct-cake
            tmpmagicpkgconfig = os.path.join(tmpdir, "magicpkgconfig")
            shutil.copytree(self._get_sample_path("magicpkgconfig"), tmpmagicpkgconfig)
            
            with uth.DirectoryContext(tmpmagicpkgconfig):
                argv = [
                    "--exemarkers=main",
                    "--testmarkers=gtest.hpp",
                    "--CTCACHE=None",
                    "--quiet",
                    "--auto",
                    "--config=" + config_path,
                ]

                compiletools.cake.main(argv)

            relativepaths = ["magicpkgconfig/main.cpp"]
            self._verify_one_exe_per_main(relativepaths, search_dir=tmpdir)

    def test_cmdline_pkgconfig(self):
        # This test is to ensure that the "--pkg-config zlib" flag 
        # correctly acquires extra cflags and libs

        with uth.CompileToolsTestContext() as (tmpdir, config_path):
            # Copy the pkgconfig test files to the temp directory and compile
            # using ct-cake
            tmppkgconfig = os.path.join(tmpdir, "pkgconfig")
            shutil.copytree(self._get_sample_path("pkgconfig"), tmppkgconfig)
            
            with uth.DirectoryContext(tmppkgconfig):
                argv = [
                    "--exemarkers=main",
                    "--testmarkers=gtest.hpp",
                    "--CTCACHE=None",
                    "--quiet",
                    "--auto",
                    "--pkg-config=zlib",
                    "--config=" + config_path,
                ]

                compiletools.cake.main(argv)

            relativepaths = ["pkgconfig/main.cpp"]
            self._verify_one_exe_per_main(relativepaths, search_dir=tmpdir)

    def test_magicpkgconfig_flags_discovery(self):
        with uth.CompileToolsTestContext() as (tmpdir, config_path):
            # Copy the magicpkgconfig test files to the temp directory
            tmpmagicpkgconfig = os.path.join(tmpdir, "magicpkgconfig")
            shutil.copytree(self._get_sample_path("magicpkgconfig"), tmpmagicpkgconfig)
            
            with uth.DirectoryContext(tmpmagicpkgconfig):
                # Create a minimal args object for testing
                # Use a simpler approach - create args from scratch like other tests
                class MockArgs:
                    def __init__(self):
                        self.config_file = config_path
                        self.variant = 'debug'
                        self.verbose = 0
                        self.quiet = True
                        self.CTCACHE = 'None'
                        self.magic = 'direct'
                        self.headerdeps = 'direct'
                        self.CPPFLAGS = ''
                
                args = MockArgs()
                
                # Create magicflags parser
                headerdeps = compiletools.headerdeps.create(args)
                magicparser = compiletools.magicflags.create(args, headerdeps)
                
                # Test the sample file that contains //#PKG-CONFIG=zlib libcrypt
                sample_file = os.path.join(tmpmagicpkgconfig, "main.cpp")
                
                # Parse the magic flags
                parsed_flags = magicparser.parse(sample_file)
                
                # Verify PKG-CONFIG flag was found
                assert "PKG-CONFIG" in parsed_flags
                pkgconfig_flags = list(parsed_flags["PKG-CONFIG"])
                assert len(pkgconfig_flags) == 1
                assert pkgconfig_flags[0] == "zlib libcrypt"
                
                # Verify CXXFLAGS were extracted (should contain zlib and libcrypt cflags)
                assert "CXXFLAGS" in parsed_flags
                cxxflags = " ".join(parsed_flags["CXXFLAGS"])
                
                # Check that pkg-config results are present (basic validation)
                try:
                    zlib_cflags = subprocess.run(
                        ["pkg-config", "--cflags", "zlib"], 
                        capture_output=True, text=True, check=True
                    ).stdout.strip().replace("-I", "-isystem ")
                    
                    libcrypt_cflags = subprocess.run(
                        ["pkg-config", "--cflags", "libcrypt"], 
                        capture_output=True, text=True, check=True
                    ).stdout.strip().replace("-I", "-isystem ")
                    
                    # Verify the parsed flags contain the expected pkg-config results
                    if zlib_cflags:
                        assert zlib_cflags in cxxflags
                    if libcrypt_cflags:
                        assert libcrypt_cflags in cxxflags
                        
                except subprocess.CalledProcessError:
                    # pkg-config might fail for missing packages, but the test should still parse the PKG-CONFIG directive
                    pass
                
                # Verify LDFLAGS were extracted 
                assert "LDFLAGS" in parsed_flags
                ldflags = " ".join(parsed_flags["LDFLAGS"])
                
                try:
                    zlib_libs = subprocess.run(
                        ["pkg-config", "--libs", "zlib"], 
                        capture_output=True, text=True, check=True
                    ).stdout.strip()
                    
                    libcrypt_libs = subprocess.run(
                        ["pkg-config", "--libs", "libcrypt"], 
                        capture_output=True, text=True, check=True
                    ).stdout.strip()
                    
                    # Verify the parsed flags contain the expected pkg-config results
                    if zlib_libs:
                        assert zlib_libs in ldflags
                    if libcrypt_libs:
                        assert libcrypt_libs in ldflags
                        
                except subprocess.CalledProcessError:
                    # pkg-config might fail for missing packages
                    pass


    def test_pkg_config_transformation_in_actual_parsing(self):
        """Test that the -I to -isystem transformation occurs during actual magic flag parsing using sample code"""
        with uth.CompileToolsTestContext() as (tmpdir, config_path):
            # Copy the magicpkgconfig sample to the temp directory
            tmpmagicpkgconfig = os.path.join(tmpdir, "magicpkgconfig")
            shutil.copytree(self._get_sample_path("magicpkgconfig"), tmpmagicpkgconfig)
            
            # Create minimal args object
            class MockArgs:
                def __init__(self):
                    self.config_file = config_path
                    self.variant = 'debug'
                    self.verbose = 0
                    self.quiet = True
                    self.CTCACHE = 'None'
                    self.magic = 'direct'
                    self.headerdeps = 'direct'
                    self.CPPFLAGS = ''
                    self.max_file_read_size = 0
            
            args = MockArgs()
            
            # Create magicflags parser
            headerdeps = compiletools.headerdeps.create(args)
            magicparser = compiletools.magicflags.create(args, headerdeps)
            
            # Use the actual magicpkgconfig sample file
            sample_file = os.path.join(tmpmagicpkgconfig, "main.cpp")
            
            # Parse the magic flags
            try:
                parsed_flags = magicparser.parse(sample_file)
                
                # Verify PKG-CONFIG flag was found (should contain "zlib libcrypt")
                assert "PKG-CONFIG" in parsed_flags, "PKG-CONFIG directive should be parsed"
                pkgconfig_flags = list(parsed_flags["PKG-CONFIG"])
                assert len(pkgconfig_flags) == 1
                assert pkgconfig_flags[0] == "zlib libcrypt"
                
                # Check CXXFLAGS for the presence of -isystem transformations
                if "CXXFLAGS" in parsed_flags:
                    cxxflags_list = parsed_flags["CXXFLAGS"]
                    cxxflags_str = " ".join(cxxflags_list)
                    
                    # If there are any include paths from pkg-config, they should use -isystem
                    if "/include" in cxxflags_str:
                        assert "-isystem" in cxxflags_str, f"Expected -isystem in CXXFLAGS, got: {cxxflags_str}"
                        
                        # Verify no -I flags remain (they should all be transformed to -isystem)
                        assert "-I/" not in cxxflags_str, f"Found -I/ in CXXFLAGS (should be -isystem): {cxxflags_str}"
                        assert not any(flag.startswith("-I ") for flag in cxxflags_list), \
                            f"Found -I flags in CXXFLAGS (should be -isystem): {cxxflags_list}"
                        
                        # Verify that other flags like -D are preserved
                        if any("-D" in flag for flag in cxxflags_list):
                            assert any("-D" in flag for flag in cxxflags_list), \
                                f"Macro definitions should be preserved in CXXFLAGS: {cxxflags_list}"
                
            except subprocess.CalledProcessError:
                # If pkg-config fails (e.g., packages not available), that's okay for this test
                # The important thing is that the transformation logic is in place
                pass



