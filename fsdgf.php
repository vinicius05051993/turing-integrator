<?php
namespace Nectar\Cupom\Controller\Adminhtml\Report;

use Magento\Backend\App\Action;
use Magento\Framework\App\ActionInterface;
use Magento\Framework\App\Filesystem\DirectoryList;
use Magento\Framework\App\Response\Http\FileFactory;
use Magento\Framework\DB\Select as DbSelect;
use Magento\Framework\Session\SessionManagerInterface;
use Magento\Framework\Stdlib\DateTime\TimezoneInterface;
use Magento\Sales\Model\ResourceModel\Order\Item\CollectionFactory as OrderItemCollection;
use Magento\SalesRule\Model\ResourceModel\Coupon\CollectionFactory as CouponCollection;
use Nectar\Cupom\Helper\GetTotalCupons;
use Nectar\Cupom\Model\ResourceModel\CouponManagementPerSchool\Grid\CollectionFactory as CouponManagementPerSchoolCollection;
use Nectar\EscolasAdmin\Model\ResourceModel\Escolas\CollectionFactory as SchoolsCollection;

/**
 * Exporta o relatório de cupons por escola em CSV.
 */
class ExportCouponManagementPerSchoolCsv implements ActionInterface
{
    const ADMIN_RESOURCE = 'Magento_Logging::magento_logging_events';

    /** @var FileFactory */
    protected $fileFactory;
    /** @var DirectoryList */
    protected $directoryList;
    /** @var SessionManagerInterface */
    protected $sessionManager;
    /** @var TimezoneInterface */
    protected $timezone;

    /** @var CouponManagementPerSchoolCollection */
    protected $couponManagementPerSchoolCollection;
    /** @var CouponCollection */
    protected $couponCollection;
    /** @var GetTotalCupons */
    protected $getTotalCoupon;
    /** @var OrderItemCollection */
    protected $orderItemCollection;
    /** @var SchoolsCollection */
    protected $schoolCollection;

    // Caches e agregados pré-carregados
    protected $schoolsCache = [];      // [code => nome]
    protected $couponCountByRule = []; // [rule_id => qtd_cupons]
    protected $totalsByRule = [];      // [rule_id => ['total'=>int,'used'=>int,'has_unlimited'=>bool]]
    protected $orderItemCount = [];    // [order_id => qtd_itens]

    public function __construct(
        Action\Context $context,
        FileFactory $fileFactory,
        DirectoryList $directoryList,
        SessionManagerInterface $sessionManager,
        TimezoneInterface $timezone,
        CouponManagementPerSchoolCollection $couponManagementPerSchoolCollection,
        CouponCollection $couponCollection,
        GetTotalCupons $getTotalCoupon,
        OrderItemCollection $orderItemCollection,
        SchoolsCollection $schoolCollection
    ) {
        $this->fileFactory = $fileFactory;
        $this->directoryList = $directoryList;
        $this->sessionManager = $sessionManager;
        $this->timezone = $timezone;
        $this->couponManagementPerSchoolCollection = $couponManagementPerSchoolCollection;
        $this->couponCollection = $couponCollection;
        $this->getTotalCoupon = $getTotalCoupon;
        $this->orderItemCollection = $orderItemCollection;
        $this->schoolCollection = $schoolCollection;
    }

    /**
     * Gera o CSV e retorna o download.
     */
    public function execute()
    {
        $fileName = 'relatorio-cupom.csv';
        $filePath = $this->directoryList->getPath(DirectoryList::MEDIA) . '/' . $fileName;

        $handle = fopen($filePath, 'w');
        if ($handle === false) {
            // Fallback simples: não conseguiu abrir arquivo
            throw new \RuntimeException('Não foi possível criar o arquivo CSV.');
        }

        // Cabeçalho do CSV
        fputcsv($handle, [
            'Nº do pedido',
            'Código do Cupom',
            'Escolas',
            'Pedido criado em',
            'Data utilização válido de',
            'Válido até',
            'CPF/CNPJ',
            'Usos por cliente',
            'Usos por cupom',
            'Usos permitidos',
            'Número de usos',
            'Disponível',
            'Qtd. itens no pedido',
            'Descrição',
            'Qtd. do Desconto',
            'Tipo de desconto',
        ]);

        // Monta a collection base (respeitando filtros da UI)
        $collection = $this->couponManagementPerSchoolCollection->create();

        $filters = $this->sessionManager->getFilterToExportCouponManagementPerSchool();
        if ($filters && is_array($filters)) {
            foreach ($filters as $filter) {
                $collection->addFieldToFilter($filter['field'], [$filter['condition'] => $filter['value']]);
            }
        }

        // Pré-carrega agregados (evita N+1 queries)
        $this->preloadAggregates($collection);

        // Escreve linhas do CSV
        foreach ($collection as $item) {
            $ruleId = (int) $item->getRuleId();
            $orderId = (int) $item->getEntityId();

            $row = [
                (string) $item->getIncrementId(),
                (string) $item->getCode(),
                (string) $this->getSchoolNameByCode($item->getSchoolSelect()),
                (string) $item->getCreatedAt(),
                (string) $item->getFromDate(),
                (string) $item->getToDate(),
                (string) $item->getTaxvat(),
                (string) $item->getUsesPerCustomer(),
                (string) $item->getUsesPerCoupon(),
                (string) $this->getPermittedUses($ruleId, $item->getUsesPerCoupon()),
                (string) $this->getTimesUsed($ruleId),
                (string) $this->getAvailable($ruleId),
                (string) ($this->orderItemCount[$orderId] ?? 0),
                (string) $item->getDescription(),
                (string) $item->getDiscountAmount(),
                (string) $item->getSimpleAction(),
            ];

            fputcsv($handle, $row);
        }

        fclose($handle);

        return $this->fileFactory->create(
            $fileName,
            ['type' => 'filename', 'value' => $fileName, 'rm' => true],
            DirectoryList::MEDIA
        );
    }

    /**
     * Pré-carrega agregados necessários para o relatório.
     * - Regra (rule_id), Pedido (entity_id), Escolas (school_select)
     * - Contagem de cupons por regra
     * - Totais usados/gerados por regra
     * - Itens por pedido
     * - Cache de nomes de escolas
     */
    protected function preloadAggregates($collection): void
    {
        // Corrigido: qualifica colunas e usa aliases estáveis (evita 'main_table.rule_id' inexistente)
        $rows = $this->getDistinctRows($collection, [
            'rule_id'       => 'sr.rule_id',
            'entity_id'     => 'main_table.entity_id',
            'school_select' => 'main_table.school_select',
        ]);

        $ruleIds = [];
        $orderIds = [];
        $schoolCodes = [];

        foreach ($rows as $r) {
            if (!empty($r['rule_id'])) {
                $ruleIds[(int) $r['rule_id']] = (int) $r['rule_id'];
            }
            if (!empty($r['entity_id'])) {
                $orderIds[(int) $r['entity_id']] = (int) $r['entity_id'];
            }
            if (!empty($r['school_select']) && $r['school_select'] !== 'empty') {
                $codes = array_filter(array_map('trim', explode(',', (string) $r['school_select'])));
                foreach ($codes as $c) {
                    $schoolCodes[$c] = $c;
                }
            }
        }

        // Contagem de cupons por rule_id
        if ($ruleIds) {
            $couponConn = $this->couponCollection->create()->getConnection();
            $couponSel = clone $this->couponCollection->create()->getSelect();
            $couponSel->reset(DbSelect::COLUMNS);
            $couponSel->columns(['rule_id', 'cnt' => 'COUNT(*)']);
            $couponSel->where('rule_id IN (?)', array_values($ruleIds));
            $couponSel->group('rule_id');

            $rows = $couponConn->fetchAll($couponSel);
            foreach ($rows as $row) {
                $this->couponCountByRule[(int) $row['rule_id']] = (int) $row['cnt'];
            }
        }

        // Qtd de itens por pedido (exclui bundle)
        if ($orderIds) {
            $itemConn = $this->orderItemCollection->create()->getConnection();
            $itemSel = clone $this->orderItemCollection->create()->getSelect();
            $itemSel->reset(DbSelect::COLUMNS);
            $itemSel->columns(['order_id', 'qty' => 'COUNT(item_id)']);
            $itemSel->where('product_type <> ?', 'bundle');
            $itemSel->where('order_id IN (?)', array_values($orderIds));
            $itemSel->group('order_id');

            $rows = $itemConn->fetchAll($itemSel);
            foreach ($rows as $row) {
                $this->orderItemCount[(int) $row['order_id']] = (int) $row['qty'];
            }
        }

        // Totais por rule_id via GetTotalCupons::getTotals()
        $this->totalsByRule = [];
        $totals = $this->getTotalCoupon->getTotals();
        foreach ($ruleIds as $rid) {
            $data = $totals[$rid] ?? $totals[(string) $rid] ?? null;
            $this->totalsByRule[$rid] = [
                'total'         => (int) ($data['total'] ?? 0),
                'used'          => (int) ($data['total usados'] ?? 0),
                'has_unlimited' => false,
            ];
        }

        // Detecta regras com cupons ilimitados (usage_limit IS NULL)
        if ($ruleIds) {
            $couponColl = $this->couponCollection->create();
            $conn = $couponColl->getConnection();
            $sel = clone $couponColl->getSelect();
            $sel->reset(DbSelect::COLUMNS);
            $sel->columns([
                'rule_id',
                'unlimited' => new \Zend_Db_Expr('SUM(CASE WHEN usage_limit IS NULL THEN 1 ELSE 0 END)'),
            ]);
            $sel->where('rule_id IN (?)', array_values($ruleIds));
            $sel->group('rule_id');

            $rows = $conn->fetchAll($sel);
            foreach ($rows as $row) {
                $rid = (int) $row['rule_id'];
                if (!isset($this->totalsByRule[$rid])) {
                    $this->totalsByRule[$rid] = ['total' => 0, 'used' => 0, 'has_unlimited' => false];
                }
                $this->totalsByRule[$rid]['has_unlimited'] = ((int) $row['unlimited']) > 0;
            }
        }

        // Cache de nomes das escolas
        if ($schoolCodes) {
            $schools = $this->schoolCollection
                ->create()
                ->addFieldToFilter('code', ['in' => array_values($schoolCodes)]);

            foreach ($schools as $s) {
                $code = (string) $s->getData('code');
                $this->schoolsCache[$code] = $s->getNome();
            }
        }
    }

    /**
     * Retorna linhas distintas qualificando colunas e resetando GROUP BY.
     * Aceita:
     * - ['alias' => 'tabela.coluna'] para colunas já qualificadas.
     * - ['coluna', ...] e qualifica com 'main_table' quando aplicável.
     *
     * @return array<int, array<string, mixed>>
     */
    private function getDistinctRows($collection, array $columns): array
    {
        $conn = $collection->getConnection();
        $select = clone $collection->getSelect();

        $fromParts = $select->getPart(\Zend_Db_Select::FROM);
        $baseAlias = isset($fromParts['main_table']) ? 'main_table' : (array_keys($fromParts)[0] ?? null);

        // Monta especificação de colunas com alias estável
        $isAssoc = array_keys($columns) !== range(0, count($columns) - 1);
        $colsSpec = [];

        if ($isAssoc) {
            foreach ($columns as $alias => $expr) {
                $colsSpec[$alias] = $expr;
            }
        } else {
            foreach ($columns as $c) {
                $colsSpec[$c] = (strpos($c, '.') !== false || !$baseAlias) ? $c : "{$baseAlias}.{$c}";
            }
        }

        // Limpa colunas e GROUP para evitar conflitos
        $select->reset(DbSelect::COLUMNS);
        $select->reset(DbSelect::GROUP);

        // Seleciona e agrupa exatamente pelos mesmos exprs
        $select->columns($colsSpec);
        $select->group(array_values($colsSpec));

        $rows = $conn->fetchAll($select);

        // Normaliza chaves (quando usamos aliases, já estão corretas)
        $normalized = [];
        foreach ($rows as $r) {
            $nr = [];
            foreach ($r as $k => $v) {
                $key = (strpos($k, '.') !== false) ? explode('.', $k)[1] : $k;
                $nr[$key] = $v;
            }
            $normalized[] = $nr;
        }

        return $normalized;
    }

    /**
     * Converte uma lista de códigos de escola em nomes, com cache.
     */
    public function getSchoolNameByCode($schoolSelect): string
    {
        if ($schoolSelect === 'empty' || $schoolSelect === null || $schoolSelect === '') {
            return 'Todas as escolas';
        }

        $codes = array_filter(array_map('trim', explode(',', (string) $schoolSelect)));
        $names = [];

        foreach ($codes as $code) {
            $names[] = $this->schoolsCache[$code] ?? $code;
        }

        return implode(', ', $names);
    }

    /**
     * Usos permitidos = (qtd. cupons gerados para a regra) * (usos por cupom).
     */
    public function getPermittedUses(int $ruleId, $usesPerCoupon): string
    {
        $qty = $this->couponCountByRule[$ruleId] ?? 0;
        return ($qty && $usesPerCoupon) ? (string) ($qty * (int) $usesPerCoupon) : '';
    }

    /**
     * Número de usos acumulados (proveniente de GetTotalCupons).
     */
    public function getTimesUsed(int $ruleId): string
    {
        return (string) ($this->totalsByRule[$ruleId]['used'] ?? 0);
    }

    /**
     * Disponível = total gerado - total usado.
     * Se houver qualquer cupom ilimitado na regra, retorna vazio.
     */
    public function getAvailable(int $ruleId): string
    {
        if (!isset($this->totalsByRule[$ruleId])) {
            return '';
        }

        if (!empty($this->totalsByRule[$ruleId]['has_unlimited'])) {
            return '';
        }

        $total = (int) ($this->totalsByRule[$ruleId]['total'] ?? 0);
        $used = (int) ($this->totalsByRule[$ruleId]['used'] ?? 0);

        return (string) max(0, $total - $used);
    }
}