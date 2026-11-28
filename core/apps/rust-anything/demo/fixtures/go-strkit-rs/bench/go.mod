module bench

go 1.22

require (
	example.com/strkit v0.0.0
	rust-anything.local/strkit_rs v0.0.0
)

replace example.com/strkit => ../../../../tests/fixtures/go
replace rust-anything.local/strkit_rs => ../go
