# Golang attach release artifacts

This action attaches the desired binaries as artifacts on a github release.
It is meant to be used on push tag events ( needs to find a valid tag in the refs )
and needs the [actions/checkout](https://github.com/actions/checkout) ( depends 
on the GITHUB_EVENT_PATH output )

## Inputs

### `go_files`

**Required** Space separated list of the go files to build

### `binaries`

**Required** Space separated list of binaries to attach. Binaries map 1 to 1 with the go_files and must be of the same length.

### `linux_build_variants`

The linux build variants. Defaults to `"386 amd64 arm arm64"`.

### `linux_build_variants`

The darwin (Mac OS) build variants. Defaults to `"amd64"`.

## Example usage

```````
    - name: checkout master
      uses: actions/checkout@master

    - name: attach release artifacts
      uses: sestus/golang-attach-release-artifacts@v1
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        go_files: 'cmd/bin1.go cmd/bin2.go '
        binaries: 'binary1 binary2'
```