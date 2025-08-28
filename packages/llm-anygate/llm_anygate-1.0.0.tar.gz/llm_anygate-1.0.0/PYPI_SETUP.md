# PyPI Publishing Setup with GitHub Actions

## 🎉 Setup Complete!

Your repository is now configured to automatically publish to PyPI when you create a GitHub release. Here's what was set up:

### ✅ What's Been Configured

1. **GitHub Secrets**: Your PyPI API token from `.env` has been added as a GitHub repository secret
2. **GitHub Environments**: Created `pypi` and `testpypi` environments for secure publishing
3. **GitHub Actions Workflow**: Created `.github/workflows/publish-pypi.yml` for automated publishing

### 🚀 How to Publish a Release

To publish a new version to PyPI, follow these steps:

1. **Update Version**: Update the version in `pyproject.toml`
2. **Create Git Tag**: 
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```
3. **Create GitHub Release**: The workflow will trigger and automatically:
   - Build the Python package
   - Publish to PyPI
   - Create signed attestations
   - Upload artifacts to the GitHub release

### 🔧 Workflow Details

The workflow includes these jobs:
- **Build**: Creates wheel and source distribution
- **Publish to PyPI**: Uploads to PyPI (only on tagged releases)
- **Publish to TestPyPI**: Uploads to TestPyPI for testing
- **GitHub Release**: Signs packages and uploads to GitHub release

### 🛡️ Security Features

- **Environment Protection**: Uses GitHub environments for secure publishing
- **Sigstore Signing**: Automatically signs packages with Sigstore
- **Separate Build/Publish**: Builds once, publishes the same artifacts

### 📝 Next Steps (Optional)

#### Option 1: Use TestPyPI for Testing
If you want to test releases on TestPyPI first:

1. Get a TestPyPI API token from https://test.pypi.org/manage/account/token/
2. Add it as a GitHub secret:
   ```bash
   gh secret set TEST_PYPI_API_TOKEN --body "YOUR_TESTPYPI_TOKEN"
   ```

#### Option 2: Switch to Trusted Publishing (Recommended)
For enhanced security, consider switching to Trusted Publishing:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new trusted publisher:
   - **Repository**: `igamenovoer/llm-anygate`
   - **Workflow filename**: `publish-pypi.yml`
   - **Environment name**: `pypi`
3. Remove the password from the workflow (it will use OIDC automatically)

### 🔍 Monitoring

- Check workflow runs in the **Actions** tab
- Monitor publishing status in the **Environments** section
- View published packages at https://pypi.org/project/llm-anygate/

### 🐛 Troubleshooting

- **Build failures**: Check Python version compatibility in `pyproject.toml`
- **Publishing failures**: Verify your PyPI API token hasn't expired
- **Permission errors**: Ensure the GitHub environments are properly configured

## 📚 Resources

- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)